import json
from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest
import requests

from tests import assert_lines


@pytest.mark.parametrize("args", [[], ["default"]])
def test_not_in_project(args, script_runner):
    ret = script_runner.run(["scrapyd-deploy", *args])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Error: no Scrapy project found in this location")
    assert not ret.success


def test_too_many_arguments(script_runner, project):
    ret = script_runner.run(["scrapyd-deploy", "mytarget", "extra"])

    assert ret.stdout == ""
    assert_lines(
        ret.stderr,
        dedent(
            """\
            usage: scrapyd-deploy [-h] [-p PROJECT] [-v VERSION] [-a] [-d] [--egg FILE]
                                  [--build-egg FILE] [--include-dependencies]
                                  [TARGET]
            scrapyd-deploy: error: unrecognized arguments: extra
            """
        ),
    )
    assert not ret.success


def test_missing_url(script_runner, conf_no_url):
    ret = script_runner.run(["scrapyd-deploy", "mytarget"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, [r"Packing version \d+", "Error: Missing url for project"])
    assert not ret.success


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
