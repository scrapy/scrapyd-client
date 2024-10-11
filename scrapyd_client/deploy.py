import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from argparse import ArgumentParser
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth
from scrapy.utils.conf import closest_scrapy_cfg
from scrapy.utils.project import inside_project

from scrapyd_client.utils import get_auth, get_config

_SETUP_PY_TEMPLATE = """
# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'project',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = %(settings)s']},
)
""".lstrip()


def parse_args():
    parser = ArgumentParser(description="Deploy Scrapy project to Scrapyd server")
    parser.add_argument("target", nargs="?", default="default", metavar="TARGET")
    parser.add_argument("-p", "--project", help="the project name in the TARGET")
    parser.add_argument("-v", "--version", help="the version to deploy. Defaults to current timestamp")
    parser.add_argument("-l", "--list-targets", action="store_true", help="list available targets")
    parser.add_argument("-a", "--deploy-all-targets", action="store_true", help="deploy all targets")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="debug mode (do not remove build dir)",
    )
    parser.add_argument(
        "-L",
        "--list-projects",
        metavar="TARGET",
        help="list available projects in the TARGET",
    )
    parser.add_argument("--egg", metavar="FILE", help="use the given egg, instead of building it")
    parser.add_argument("--build-egg", metavar="FILE", help="only build the egg, don't deploy it")
    parser.add_argument(
        "--include-dependencies",
        action="store_true",
        help="include dependencies from requirements.txt in the egg",
    )
    return parser.parse_args()


def main():
    opts = parse_args()
    exitcode = 0
    if not inside_project():
        _log("Error: no Scrapy project found in this location")
        sys.exit(1)

    if opts.list_targets:
        for name, target in _get_targets().items():
            print("%-20s %s" % (name, target["url"]))
        return

    if opts.list_projects:
        target = _get_target(opts.list_projects)

        projects = requests.get(_url(target, "listprojects.json"), **_requests_auth(target)).json()["projects"]
        print(os.linesep.join(projects))
        return

    tmpdir = None

    if opts.build_egg:  # build egg only
        eggpath, tmpdir = _build_egg(opts)
        _log(f"Writing egg to {opts.build_egg}")
        shutil.copyfile(eggpath, opts.build_egg)
    elif opts.deploy_all_targets:
        version = None
        for target in _get_targets().values():
            if version is None:
                version = _get_version(target, opts)
            _, tmpdir = _build_egg_and_deploy_target(target, version, opts)
            _remove_tmpdir(tmpdir, opts)
    else:  # buld egg and deploy
        target = _get_target(opts.target)
        version = _get_version(target, opts)
        exitcode, tmpdir = _build_egg_and_deploy_target(target, version, opts)
        _remove_tmpdir(tmpdir, opts)

    sys.exit(exitcode)


def _remove_tmpdir(tmpdir, opts):
    if tmpdir:
        if opts.debug:
            _log(f"Output dir not removed: {tmpdir}")
        else:
            shutil.rmtree(tmpdir)


def _build_egg_and_deploy_target(target, version, opts):
    exitcode = 0
    tmpdir = None

    project = opts.project or target.get("project")
    if not project:
        raise _fail("Error: Missing project")

    if opts.egg:
        _log(f"Using egg: {opts.egg}")
        eggpath = opts.egg
    else:
        _log(f"Packing version {version}")
        eggpath, tmpdir = _build_egg(opts)

    url = _url(target, "addversion.json")
    _log(f'Deploying to project "{project}" in {url}')

    # Upload egg.
    try:
        with open(eggpath, "rb") as f:
            response = requests.post(
                _url(target, "addversion.json"),
                data={"project": project, "version": version},
                files=[("egg", ("project.egg", f))],
                **_requests_auth(target),
            )
        response.raise_for_status()
        _log(f"Server response ({response.status_code}):")
        print(response.text)
    except requests.HTTPError as e:
        _log(f"Deploy failed ({e.response.status_code}):")
        exitcode = 1
        try:
            data = e.response.json()
        except json.decoder.JSONDecodeError:
            print(e.response.text)
        else:
            if "status" in data and "message" in data:
                print(f"Status: {data['status']}")
                print(f"Message:\n{data['message']}")
            else:
                print(json.dumps(data, indent=3))
    except requests.RequestException as e:
        _log(f"Deploy failed: {e}")
        exitcode = 1

    return exitcode, tmpdir


def _log(message):
    sys.stderr.write(f"{message}{os.linesep}")


def _fail(message, code=1):
    _log(message)
    sys.exit(code)


def _get_targets():
    cfg = get_config()
    baset = dict(cfg.items("deploy")) if cfg.has_section("deploy") else {}
    targets = {}
    if "url" in baset:
        targets["default"] = baset
    for section in cfg.sections():
        if section.startswith("deploy:"):
            t = baset.copy()
            t.update(cfg.items(section))
            targets[section[7:]] = t
    return targets


def _get_target(name):
    try:
        return _get_targets()[name]
    except KeyError:
        raise _fail(f"Unknown target: {name}") from None


def _url(target, action):
    if "url" in target:
        return urljoin(target["url"], action)
    raise _fail("Error: Missing url for project")


def _get_version(target, opts):
    version = opts.version or target.get("version")
    if version == "HG":
        process = subprocess.Popen(
            ["hg", "tip", "--template", "{rev}"], stdout=subprocess.PIPE, universal_newlines=True
        )
        descriptor = f"r{process.communicate()[0]}"
        process = subprocess.Popen(["hg", "branch"], stdout=subprocess.PIPE, universal_newlines=True)
        name = process.communicate()[0].strip("\n")
        return f"{descriptor}-{name}"
    if version == "GIT":
        process = subprocess.Popen(["git", "describe"], stdout=subprocess.PIPE, universal_newlines=True)
        descriptor = process.communicate()[0].strip("\n")
        if process.wait() != 0:
            process = subprocess.Popen(
                ["git", "rev-list", "--count", "HEAD"],
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            descriptor = "r{}".format(process.communicate()[0].strip("\n"))

        process = subprocess.Popen(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        name = process.communicate()[0].strip("\n")
        return f"{descriptor}-{name}"
    if version:
        return version
    return str(int(time.time()))


def _requests_auth(target):
    if auth := get_auth(url=target["url"], username=target.get("username"), password=target.get("password", "")):
        return {"auth": HTTPBasicAuth(auth.username, auth.password)}
    return {}


def _build_egg(opts):
    closest = closest_scrapy_cfg()
    os.chdir(os.path.dirname(closest))
    if not os.path.exists("setup.py"):
        settings = get_config().get("settings", "default")
        with open("setup.py", "w") as f:
            f.write(_SETUP_PY_TEMPLATE % {"settings": settings})
    tmpdir = tempfile.mkdtemp(prefix="scrapydeploy-")

    if opts.include_dependencies:
        _log("Including dependencies from requirements.txt")
        if not os.path.isfile("requirements.txt"):
            _fail("Error: Missing requirements.txt")
        command = "bdist_uberegg"
    else:
        command = "bdist_egg"

    kwargs = {} if opts.debug else {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    subprocess.run([sys.executable, "setup.py", "clean", "-a", command, "-d", tmpdir], check=True, **kwargs)

    eggpath = glob.glob(os.path.join(tmpdir, "*.egg"))[0]
    return eggpath, tmpdir


if __name__ == "__main__":
    main()
