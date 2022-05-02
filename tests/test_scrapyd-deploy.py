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
def project_with_dependencies(project):
    with open('requirements.txt', 'w') as f:
        f.write('')


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
def conf_no_url(project):
    _write_conf_file("""\
        [deploy:mytarget]
        project = scrapydproject
    """)


@pytest.fixture
def conf_default_target(project):
    _write_conf_file("""\
        [deploy]
        url = http://localhost:6800/
        project = scrapydproject
    """)


@pytest.fixture
def conf_named_targets(project):
    # target2 is deliberately before target 1, to test ordering.
    _write_conf_file("""\
        [deploy:target2]
        url = http://localhost:6802/
        project = anotherproject

        [deploy:target1]
        url = http://localhost:6801/
        project = scrapydproject
    """)


@pytest.fixture
def conf_mixed_targets(project):
    # target2 is deliberately before target 1, to test ordering.
    _write_conf_file("""\
        [deploy]
        url = http://localhost:6800/
        project = anotherproject

        [deploy:target1]
        url = http://localhost:6801/
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


@pytest.mark.parametrize('args', [[], ['-l'], ['-L', 'default']])
def test_not_in_project(args, script_runner):
    ret = script_runner.run('scrapyd-deploy', *args)

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Error: no Scrapy project found in this location')


@pytest.mark.parametrize('args', [[], ['-l'], ['-L', 'default']])
def test_too_many_arguments(args, script_runner, project):
    ret = script_runner.run('scrapyd-deploy', 'mytarget', 'extra')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, dedent("""\
        usage: scrapyd-deploy [-h] [-p PROJECT] [-v VERSION] [-l] [-a] [-d]
                              [-L TARGET] [--egg FILE] [--build-egg FILE]
                              [--include-dependencies]
                              [TARGET]
        scrapyd-deploy: error: unrecognized arguments: extra
    """))


@pytest.mark.xfail(reason='raises KeyError')
def test_list_targets_missing_url(script_runner, conf_no_url):
    ret = script_runner.run('scrapyd-deploy', 'mytarget')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Error: Missing url for project')


def test_list_targets_with_default(script_runner, conf_mixed_targets):
    ret = script_runner.run('scrapyd-deploy', '-l')

    assert ret.success
    assertLines(ret.stdout, dedent("""\
        default              http://localhost:6800/
        target1              http://localhost:6801/
    """))
    assert ret.stderr == ''


def test_list_targets_without_default(script_runner, conf_named_targets):
    ret = script_runner.run('scrapyd-deploy', '-l')

    assert ret.success
    assertLines(ret.stdout, dedent("""\
        target2              http://localhost:6802/
        target1              http://localhost:6801/
    """))
    assert ret.stderr == ''


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


def test_deploy_missing_project(script_runner, conf_no_project):
    ret = script_runner.run('scrapyd-deploy')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Error: Missing project')


@pytest.mark.xfail(reason='raises KeyError')
def test_deploy_missing_url(script_runner, conf_no_url):
    ret = script_runner.run('scrapyd-deploy', 'mytarget')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Error: Missing url for project')


def test_build_egg(script_runner, project):
    ret = script_runner.run('scrapyd-deploy', '--build-egg', 'myegg.egg')

    assert ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, 'Writing egg to myegg.egg')


def test_build_egg_inc_dependencies_no_dep(script_runner, project):
    ret = script_runner.run('scrapyd-deploy', '--include-dependencies', '--build-egg', 'myegg-deps.egg')

    assert not ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, dedent("""\
        Including dependencies from requirements.txt
        Error: Missing requirements.txt
    """))


def test_build_egg_inc_dependencies_with_dep(script_runner, project_with_dependencies):
    ret = script_runner.run('scrapyd-deploy', '--include-dependencies', '--build-egg', 'myegg-deps.egg')

    assert ret.success
    assert ret.stdout == ''
    assertLines(ret.stderr, dedent("""\
        Including dependencies from requirements.txt
        Writing egg to myegg-deps.egg
    """))


def test_deploy_success(script_runner, conf_default_target):
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
def test_deploy_httperror(content, expected, script_runner, conf_default_target):
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


def test_deploy_urlerror(script_runner, conf_default_target):
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
