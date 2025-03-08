import sys
from argparse import ArgumentParser
from textwrap import indent
from traceback import print_exc

import requests
from scrapy.utils.project import inside_project

import scrapyd_client.deploy
from scrapyd_client.exceptions import ErrorResponse, MalformedResponse
from scrapyd_client.pyclient import ScrapydClient
from scrapyd_client.utils import _get_targets, get_config

ISSUE_TRACKER_URL = "https://github.com/scrapy/scrapyd-client/issues"


def _get_client(args):
    target = _get_targets()[args.target]

    return ScrapydClient(target.get("url"), target.get("username"), password=target.get("password", ""))


def deploy(args):  # noqa: ARG001
    """Deploy a Scrapy project to a Scrapyd instance. For help, invoke scrapyd-deploy."""
    sys.argv.pop(1)
    scrapyd_client.deploy.main()


def targets(args):  # noqa: ARG001
    """List all targets."""
    for name, target in _get_targets().items():
        print("%-20s %s" % (name, target["url"]))


def projects(args):
    """List all projects deployed on a Scrapyd instance."""
    client = _get_client(args)

    if projects := client.projects():
        print("\n".join(projects))


def schedule(args):
    """Schedule the specified spider(s)."""
    client = _get_client(args)
    job_args = [(key, value) for job_arg in args.arg for key, value in job_arg.split("=", 1)]

    for project in client.projects(args.project):
        for spider in client.spiders(project, args.spider):
            job_id = client.schedule(project, spider, job_args)
            print(f"{project} / {spider} => {job_id}")


def spiders(args):
    """List all spiders for the given project(s)."""
    client = _get_client(args)

    for project in client.projects(args.project):
        spiders = client.spiders(project)
        if not args.verbose:
            print(f"{project}:")
            if spiders:
                print(indent("\n".join(spiders), "  "))
            else:
                print("  No spiders.")
        elif spiders:
            print("\n".join(f"{project} {spider}" for spider in spiders))


def parse_cli_args(args):
    cfg = get_config()

    project_kwargs = {
        "metavar": "PROJECT",
        "required": True,
        "help": "Specifies the project, can be a globbing pattern.",
    }
    if project_default := cfg.get("deploy", "project", fallback=None):
        project_kwargs["default"] = project_default

    description = "A command line interface for Scrapyd."
    mainparser = ArgumentParser(description=description)
    subparsers = mainparser.add_subparsers()

    parser = subparsers.add_parser("deploy", description=deploy.__doc__)
    parser.set_defaults(action=deploy)

    parser = subparsers.add_parser("targets", description=targets.__doc__)
    parser.set_defaults(action=targets)

    parser = subparsers.add_parser("projects", description=projects.__doc__)
    parser.set_defaults(action=projects)
    parser.add_argument("-t", "--target", default="default", help="Specifies the target Scrapyd server by name.")

    parser = subparsers.add_parser("schedule", description=schedule.__doc__)
    parser.set_defaults(action=schedule)
    parser.add_argument("-t", "--target", default="default", help="Specifies the target Scrapyd server by name.")
    parser.add_argument("-p", "--project", **project_kwargs)
    parser.add_argument(
        "spider",
        metavar="SPIDER",
        help="Specifies the spider, can be a globbing pattern.",
    )
    parser.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Additional argument (key=value), can be specified multiple times.",
    )

    parser = subparsers.add_parser("spiders", description=spiders.__doc__)
    parser.set_defaults(action=spiders)
    parser.add_argument("-t", "--target", default="default", help="Specifies the target Scrapyd server by name.")
    parser.add_argument("-p", "--project", **project_kwargs)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Prints project's and spider's name in each line, intended for " "processing stdout in scripts.",
    )

    # If 'deploy' is moved to this module, these lines can be removed. (b9ba799)
    parsed_args, _ = mainparser.parse_known_args(args)
    if getattr(parsed_args, "action", None) is not deploy:
        parsed_args = mainparser.parse_args(args)

    if not hasattr(parsed_args, "action"):
        mainparser.print_help()
        raise SystemExit(0)

    return parsed_args


def main():
    if not inside_project():
        print("Error: no Scrapy project found in this location", file=sys.stderr)
        sys.exit(1)

    max_response_length = 120
    try:
        args = parse_cli_args(sys.argv[1:])
        args.action(args)
    except KeyboardInterrupt:
        print("Aborted due to keyboard interrupt.")
        exit_code = 0
    except SystemExit as e:
        exit_code = e.code
    except requests.ConnectionError as e:
        print(f"Failed to connect to target ({args.target}):")
        print(e)
        exit_code = 1
    except ErrorResponse as e:
        print("Scrapyd responded with an error:")
        print(e)
        exit_code = 1
    except MalformedResponse as e:
        text = str(e)
        if len(text) > max_response_length:
            text = f"{text[:50]} [...] {text[-50:]}"
        print("Received a malformed response:")
        print(text)
        exit_code = 1
    except Exception:  # noqa: BLE001
        print(f"Caught unhandled exception, please report at {ISSUE_TRACKER_URL}")
        print_exc()
        exit_code = 3
    else:
        exit_code = 0
    finally:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
