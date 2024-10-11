import os
from textwrap import dedent

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
