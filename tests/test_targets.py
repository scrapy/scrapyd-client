from textwrap import dedent

from tests import assert_lines


def test_not_in_project(script_runner):
    ret = script_runner.run(["scrapyd-client", "targets"])

    assert ret.stdout == ""
    assert_lines(ret.stderr, "Error: no Scrapy project found in this location")
    assert not ret.success


def test_too_many_arguments(script_runner, project):
    ret = script_runner.run(["scrapyd-client", "targets", "extra"])

    assert ret.stdout == ""
    assert_lines(
        ret.stderr,
        dedent(
            """\
            usage: scrapyd-client [-h] {deploy,targets,projects,schedule,spiders} ...
            scrapyd-client: error: unrecognized arguments: extra
            """
        ),
    )
    assert not ret.success


def test_list_targets_with_default(script_runner, conf_mixed_targets):
    ret = script_runner.run(["scrapyd-client", "targets"])

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
    ret = script_runner.run(["scrapyd-client", "targets"])

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
