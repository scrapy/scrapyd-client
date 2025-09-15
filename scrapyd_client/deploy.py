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
from rich.console import Console
from scrapy.utils.conf import closest_scrapy_cfg
from scrapy.utils.project import inside_project

from scrapyd_client.utils import _get_targets, get_auth, get_config

console = Console()
console_err = Console(stderr=True)

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
    parser.add_argument("-a", "--deploy-all-targets", action="store_true", help="deploy all targets")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="debug mode (do not remove build dir)",
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
        console_err.print("[red]Error: no Scrapy project found in this location[/red]")
        sys.exit(1)

    tmpdir = None

    if opts.build_egg:  # build egg only
        eggpath, tmpdir = _build_egg(opts)
        console_err.print(f"[blue]Writing egg to {opts.build_egg}[/blue]")
        shutil.copyfile(eggpath, opts.build_egg)
    elif opts.deploy_all_targets:
        version = None
        for target in _get_targets().values():
            if version is None:
                version = _get_version(target, opts)
            _, tmpdir = _build_egg_and_deploy_target(target, version, opts)
            _remove_tmpdir(tmpdir, opts)
    else:  # build egg and deploy
        try:
            target = _get_targets()[opts.target]
        except KeyError:
            console_err.print(f"[red]Unknown target: {opts.target}[/red]")
            sys.exit(1)

        version = _get_version(target, opts)
        exitcode, tmpdir = _build_egg_and_deploy_target(target, version, opts)
        _remove_tmpdir(tmpdir, opts)

    sys.exit(exitcode)


def _remove_tmpdir(tmpdir, opts):
    if tmpdir:
        if opts.debug:
            console_err.print(f"[yellow]Output dir not removed: {tmpdir}[/yellow]")
        else:
            shutil.rmtree(tmpdir)


def _build_egg_and_deploy_target(target, version, opts):
    exitcode = 0
    tmpdir = None

    project = opts.project or target.get("project")
    if not project:
        console_err.print("[red]Error: Missing project[/red]")
        sys.exit(1)

    if opts.egg:
        console_err.print(f"[blue]Using egg: {opts.egg}[/blue]")
        eggpath = opts.egg
    else:
        console_err.print(f"[blue]Packing version {version}[/blue]")
        eggpath, tmpdir = _build_egg(opts)

    url = _url(target, "addversion.json")
    console_err.print(f'[bold blue]Deploying to project "{project}" in {url}[/bold blue]')

    # Upload egg.
    kwargs = {}
    if auth := get_auth(url=target["url"], username=target.get("username"), password=target.get("password", "")):
        kwargs["auth"] = HTTPBasicAuth(auth.username, auth.password)

    try:
        with open(eggpath, "rb") as f:
            response = requests.post(
                _url(target, "addversion.json"),
                data={"project": project, "version": version},
                files=[("egg", ("project.egg", f))],
                **kwargs,
            )
        response.raise_for_status()
        console_err.print(f"[green]✓ Server response ({response.status_code}):[/green]")
        console.print(response.text)
    except requests.HTTPError as e:
        console_err.print(f"[red]✗ Deploy failed ({e.response.status_code}):[/red]")
        exitcode = 1
        try:
            data = e.response.json()
        except json.decoder.JSONDecodeError:
            console.print(f"[dim]{e.response.text}[/dim]")
        else:
            if "status" in data and "message" in data:
                console.print(f"Status: [yellow]{data['status']}[/yellow]")
                console.print(f"Message:\n[dim]{data['message']}[/dim]")
            else:
                console.print(json.dumps(data, indent=3))
    except requests.RequestException as e:
        console_err.print(f"[red]✗ Deploy failed: {e}[/red]")
        exitcode = 1

    return exitcode, tmpdir


def _url(target, action):
    if "url" in target:
        return urljoin(target["url"], action)
    console_err.print("[red]Error: Missing url for project[/red]")
    sys.exit(1)


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


def _build_egg(opts):
    closest = closest_scrapy_cfg()
    os.chdir(os.path.dirname(closest))
    if not os.path.exists("setup.py"):
        settings = get_config().get("settings", "default")
        with open("setup.py", "w") as f:
            f.write(_SETUP_PY_TEMPLATE % {"settings": settings})
    tmpdir = tempfile.mkdtemp(prefix="scrapydeploy-")

    if opts.include_dependencies:
        console_err.print("[blue]Including dependencies from requirements.txt[/blue]")
        if not os.path.isfile("requirements.txt"):
            console_err.print("[red]Error: Missing requirements.txt[/red]")
            sys.exit(1)
        command = "bdist_uberegg"
    else:
        command = "bdist_egg"

    kwargs = {} if opts.debug else {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    subprocess.run([sys.executable, "setup.py", "clean", "-a"], check=True, **kwargs)
    subprocess.run([sys.executable, "setup.py", command, "-d", tmpdir], check=True, **kwargs)

    eggpath = glob.glob(os.path.join(tmpdir, "*.egg"))[0]
    return eggpath, tmpdir


if __name__ == "__main__":
    main()
