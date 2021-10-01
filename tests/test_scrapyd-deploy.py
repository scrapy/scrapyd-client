import os
import re
from io import BytesIO
from textwrap import dedent
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest


def _write_conf_file(content):
    """
    Scrapy startproject writes a file like:

    .. code-block:: ini

        # Automatically created by: scrapy startproject
        #
        # For more information about the [deploy] section see:
        # https://scrapyd.readthedocs.io/en/latest/deploy.html

        [settings]
        default = ${project_name}.settings

        [deploy]
        #url = http://localhost:6800/
        project = ${project_name}

    See scrapy/templates/project/scrapy.cfg
    """
    with open('scrapy.cfg', 'w') as f:
        f.write(dedent("""\
            [settings]
            default = scrapyproj.settings
        """) + dedent(content))


@pytest.fixture
def project(tmpdir, script_runner):
    cwd = os.getcwd()

    p = tmpdir.mkdir('myhome')
    p.chdir()
    ret = script_runner.run('scrapy', 'startproject', 'scrapyproj')

    assert ret.success
    assert "New Scrapy project 'scrapyproj'" in ret.stdout
    assert ret.stderr == ''

    os.chdir('scrapyproj')
    yield
    os.chdir(cwd)


@pytest.fixture
def conf_empty_section_implicit_target(project):
    _write_conf_file('[deploy]')


@pytest.fixture
def conf_empty_section_explicit_target(project):
    _write_conf_file('[deploy:mytarget]')


@pytest.fixture
def conf_no_project(project):
    _write_conf_file("""\
        [deploy]
        url = http://localhost:6800/
    """)


@pytest.fixture
def conf(project):
    _write_conf_file("""\
        [deploy]
        url = http://localhost:6800/
        project = scrapydproject
    """)


def assertLines(actual, expected):
    if isinstance(expected, str):
        assert actual.splitlines() == expected.splitlines()
    else:
        lines = actual.splitlines()
        assert len(lines) == len(expected)
        for i, line in enumerate(lines):
            assert re.search(f'^{expected[i]}$', line), f'{line} does not match {expected[i]}'


def test_not_in_project(script_runner):
    ret = script_runner.run('scrapyd-deploy', '-l')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Error: no Scrapy project found in this location')


def test_too_many_arguments(script_runner, project):
    ret = script_runner.run('scrapyd-deploy', 'mytarget', 'extra')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, dedent("""\
        usage: scrapyd-deploy [-h] [-p PROJECT] [-v VERSION] [-l] [-a] [-d]
                              [-L TARGET] [--egg FILE] [--build-egg FILE]
                              [target]
        scrapyd-deploy: error: unrecognized arguments: extra
    """))


def test_unknown_target_implicit(script_runner, project):
    ret = script_runner.run('scrapyd-deploy')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Unknown target: default')


def test_unknown_target_explicit(script_runner, project):
    ret = script_runner.run('scrapyd-deploy', 'nonexistent')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Unknown target: nonexistent')


def test_empty_section_implicit_target(script_runner, conf_empty_section_implicit_target):
    ret = script_runner.run('scrapyd-deploy')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Unknown target: default')


def test_empty_section_explicit_target(script_runner, conf_empty_section_explicit_target):
    ret = script_runner.run('scrapyd-deploy', 'mytarget')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Error: Missing project')


def test_missing_project(script_runner, conf_no_project):
    ret = script_runner.run('scrapyd-deploy')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Error: Missing project')


def test_build_egg(script_runner, project):
    ret = script_runner.run('scrapyd-deploy', '--build-egg', 'myegg.egg')

    assert ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Writing egg to myegg.egg')


def test_deploy_success(script_runner, conf):
    with patch('scrapyd_client.deploy.urlopen') as mocked:
        # https://scrapyd.readthedocs.io/en/stable/api.html#addversion-json
        mocked.return_value.code = 200
        mocked.return_value.read.side_effect = lambda: b'{"status": "ok"}'

        ret = script_runner.run('scrapyd-deploy')

        assert ret.success
        assertLines(ret.stdout, '{"status": "ok"}')
        assertLines(ret.stderr, [
            r'Packing version \d+',
            r'Deploying to project "scrapydproject" in http://localhost:6800/addversion\.json',
            r'Server response \(200\):'
        ])


@pytest.mark.parametrize('content,expected', [
    (b'content', 'content'),
    (b'["content"]', '[\n   "content"\n]'),
    (b'{"status": "error", "message": "content"}', 'Status: error\nMessage:\ncontent'),
])
def test_deploy_httperror(content, expected, script_runner, conf):
    with patch('scrapyd_client.deploy.urlopen') as mocked:
        # https://scrapyd.readthedocs.io/en/stable/api.html#addversion-json
        mocked.side_effect = HTTPError(
            url='http://localhost:6800/addversion.json',
            msg='msg',
            hdrs='hdrs',
            code=404,
            fp=BytesIO(content)
        )

        ret = script_runner.run('scrapyd-deploy')

        assert not ret.success
        assertLines(ret.stdout, f'{expected}')
        assertLines(ret.stderr, [
            r'Packing version \d+',
            r'Deploying to project "scrapydproject" in http://localhost:6800/addversion\.json',
            r'Deploy failed \(404\):'
        ])


def test_deploy_urlerror(script_runner, conf):
    with patch('scrapyd_client.deploy.urlopen') as mocked:
        # https://scrapyd.readthedocs.io/en/stable/api.html#addversion-json
        mocked.side_effect = URLError(reason='content')

        ret = script_runner.run('scrapyd-deploy')

        assert not ret.success
        assert ret.stdout == ''
        assertLines(ret.stderr, [
            r'Packing version \d+',
            r'Deploying to project "scrapydproject" in http://localhost:6800/addversion\.json',
            r'Deploy failed: <urlopen error content>'
        ])
