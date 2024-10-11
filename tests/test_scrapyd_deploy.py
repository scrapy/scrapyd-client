import json
import os
import re
from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest
import requests


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
    with open("scrapy.cfg", "w") as f:
        f.write(
            dedent(
                """\
                [settings]
                default = scrapyproj.settings
                """
            )
            + dedent(content)
        )


@pytest.fixture
def project(tmpdir, script_runner):
    cwd = os.getcwd()

    p = tmpdir.mkdir("myhome")
    p.chdir()
    ret = script_runner.run(["scrapy", "startproject", "scrapyproj"])

    assert "New Scrapy project 'scrapyproj'" in ret.stdout
    assert ret.stderr == ""
    assert ret.success

    os.chdir("scrapyproj")
    yield
    os.chdir(cwd)


@pytest.fixture
def project_with_dependencies(project):
    with open("requirements.txt", "w") as f:
        f.write("")


@pytest.fixture
def conf_empty_section_implicit_target(project):
    _write_conf_file("[deploy]")


@pytest.fixture
def conf_empty_section_explicit_target(project):
    _write_conf_file("[deploy:mytarget]")


@pytest.fixture
def conf_no_project(project):
    _write_conf_file(
        """\
        [deploy]
        url = http://localhost:6800/
    """
    )


@pytest.fixture
def conf_no_url(project):
    _write_conf_file(
        """\
        [deploy:mytarget]
        project = scrapydproject
    """
    )


@pytest.fixture
def conf_default_target(project):
    _write_conf_file(
        """\
        [deploy]
        url = http://localhost:6800/
        project = scrapydproject
    """
    )


@pytest.fixture
def conf_named_targets(project):
    # target2 is deliberately before target 1, to test ordering.
    _write_conf_file(
        """\
        [deploy:target2]
        url = http://localhost:6802/
        project = anotherproject

        [deploy:target1]
        url = http://localhost:6801/
        project = scrapydproject
    """
    )


@pytest.fixture
def conf_mixed_targets(project):
    # target2 is deliberately before target 1, to test ordering.
    _write_conf_file(
        """\
        [deploy]
        url = http://localhost:6800/
        project = anotherproject

        [deploy:target1]
        url = http://localhost:6801/
        project = scrapydproject
    """
    )


def assert_lines(actual, expected):
    if isinstance(expected, str):
        assert actual.splitlines() == expected.splitlines()
    else:
        lines = actual.splitlines()
        assert len(lines) == len(expected)
        for i, line in enumerate(lines):
            assert re.search(f"^{expected[i]}$", line), f"{line} does not match {expected[i]}"


@pytest.mark.parametrize("args", [[], ["-l"], ["-L", "default"]])
def test_not_in_project(args, script_runner):
    ret = script_runner.run(["scrapyd-deploy", *args])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Error: no Scrapy project found in this location")
    assert not ret.success


@pytest.mark.parametrize("args", [[], ["-l"], ["-L", "default"]])
def test_too_many_arguments(args, script_runner, project):
    ret = script_runner.run(["scrapyd-deploy", "mytarget", "extra"])

    assert ret.stdout == ""
    assert_lines(
        ret.stderr,
        dedent(
            """\
            usage: scrapyd-deploy [-h] [-p PROJECT] [-v VERSION] [-l] [-a] [-d]
                                  [-L TARGET] [--egg FILE] [--build-egg FILE]
                                  [--include-dependencies]
                                  [TARGET]
            scrapyd-deploy: error: unrecognized arguments: extra
            """
        ),
    )
    assert not ret.success


def test_list_targets_missing_url(script_runner, conf_no_url):
    ret = script_runner.run(["scrapyd-deploy", "mytarget"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, [r"Packing version \d+", "Error: Missing url for project"])
    assert not ret.success


def test_list_targets_with_default(script_runner, conf_mixed_targets):
    ret = script_runner.run(["scrapyd-deploy", "-l"])

    assert_lines(
        ret.stdout,
        dedent(
            """\
            default              http://localhost:6800/
            target1              http://localhost:6801/
            """
        ),
    )
    assert ret.stderr == ""
    assert ret.success


def test_list_targets_without_default(script_runner, conf_named_targets):
    ret = script_runner.run(["scrapyd-deploy", "-l"])

    assert_lines(
        ret.stdout,
        dedent(
            """\
            target2              http://localhost:6802/
            target1              http://localhost:6801/
            """
        ),
    )
    assert ret.stderr == ""
    assert ret.success


def test_unknown_target_implicit(script_runner, project):
    ret = script_runner.run(["scrapyd-deploy"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Unknown target: default")
    assert not ret.success


def test_unknown_target_explicit(script_runner, project):
    ret = script_runner.run(["scrapyd-deploy", "nonexistent"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Unknown target: nonexistent")
    assert not ret.success


def test_empty_section_implicit_target(script_runner, conf_empty_section_implicit_target):
    ret = script_runner.run(["scrapyd-deploy"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Unknown target: default")
    assert not ret.success


def test_empty_section_explicit_target(script_runner, conf_empty_section_explicit_target):
    ret = script_runner.run(["scrapyd-deploy", "mytarget"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Error: Missing project")
    assert not ret.success


def test_deploy_missing_project(script_runner, conf_no_project):
    ret = script_runner.run(["scrapyd-deploy"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Error: Missing project")
    assert not ret.success


def test_deploy_missing_url(script_runner, conf_no_url):
    ret = script_runner.run(["scrapyd-deploy", "mytarget"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, [r"Packing version \d+", "Error: Missing url for project"])
    assert not ret.success


def test_build_egg(script_runner, project):
    ret = script_runner.run(["scrapyd-deploy", "--build-egg", "myegg.egg"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Writing egg to myegg.egg")
    assert ret.success


def test_build_egg_inc_dependencies_no_dep(script_runner, project):
    ret = script_runner.run(["scrapyd-deploy", "--include-dependencies", "--build-egg", "myegg-deps.egg"])

    assert ret.stdout == ""
    assert_lines(
        ret.stderr,
        dedent(
            """\
            Including dependencies from requirements.txt
            Error: Missing requirements.txt
            """
        ),
    )
    assert not ret.success


def test_build_egg_inc_dependencies_with_dep(script_runner, project_with_dependencies):
    ret = script_runner.run(["scrapyd-deploy", "--include-dependencies", "--build-egg", "myegg-deps.egg", "--debug"])

    assert ret.stdout == ""
    assert_lines(
        ret.stderr,
        dedent(
            """\
            Including dependencies from requirements.txt
            Writing egg to myegg-deps.egg
            """
        ),
    )
    assert ret.success


def test_deploy_success(script_runner, conf_default_target):
    with patch("scrapyd_client.deploy.requests.post") as mocked:
        mocked.return_value.status_code = 200
        mocked.return_value.text = '{"status": "ok"}'

        ret = script_runner.run(["scrapyd-deploy"])

        assert_lines(ret.stdout, '{"status": "ok"}')
        assert_lines(
            ret.stderr,
            [
                r"Packing version \d+",
                r'Deploying to project "scrapydproject" in http://localhost:6800/addversion\.json',
                r"Server response \(200\):",
            ],
        )
        assert ret.success


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("content", "content"),
        (["content"], '[\n   "content"\n]'),
        (
            {"status": "error", "message": "content"},
            "Status: error\nMessage:\ncontent",
        ),
    ],
)
def test_deploy_httperror(content, expected, script_runner, conf_default_target):
    with patch("scrapyd_client.deploy.requests.post") as mocked:
        response = MagicMock(status_code=404, text=content)
        if isinstance(content, (dict, list)):
            response.json.side_effect = lambda: content
        else:
            response.json.side_effect = json.decoder.JSONDecodeError("", "", 0)
        mocked.side_effect = requests.HTTPError(response=response)

        ret = script_runner.run(["scrapyd-deploy"])

        assert ret.returncode == 1
        assert_lines(ret.stdout, f"{expected}")
        assert_lines(
            ret.stderr,
            [
                r"Packing version \d+",
                r'Deploying to project "scrapydproject" in http://localhost:6800/addversion\.json',
                r"Deploy failed \(404\):",
            ],
        )


def test_deploy_urlerror(script_runner, conf_default_target):
    with patch("scrapyd_client.deploy.requests.post") as mocked:
        mocked.side_effect = requests.RequestException("content")

        ret = script_runner.run(["scrapyd-deploy"])

        assert ret.returncode == 1
        assert ret.stdout == ""
        assert_lines(
            ret.stderr,
            [
                r"Packing version \d+",
                r'Deploying to project "scrapydproject" in http://localhost:6800/addversion\.json',
                r"Deploy failed: content",
            ],
        )
