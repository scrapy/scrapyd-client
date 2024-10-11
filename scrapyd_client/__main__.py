import sys
from argparse import ArgumentParser
from textwrap import indent
from traceback import print_exc

import requests

import scrapyd_client.deploy
from scrapyd_client import lib
from scrapyd_client.exceptions import ErrorResponse, MalformedResponse
from scrapyd_client.utils import DEFAULT_TARGET_URL, get_config

INDENT_PREFIX = "  "
ISSUE_TRACKER_URL = "https://github.com/scrapy/scrapyd-client/issues"


def deploy(args):  # noqa: ARG001
    """Deploy a Scrapy project to a Scrapyd instance. For help, invoke scrapyd-deploy."""
    sys.argv.pop(1)
    scrapyd_client.deploy.main()


def projects(args):
    """List all projects deployed on a Scrapyd instance."""
    if _projects := lib.get_projects(args.target, username=args.username, password=args.password):
        print("\n".join(_projects))


def schedule(args):
    """Schedule the specified spider(s)."""
    job_args = [(x[0], x[1]) for x in (y.split("=", 1) for y in args.arg)]

    for project in lib.get_projects(args.target, args.project, username=args.username, password=args.password):
        _spiders = lib.get_spiders(
            args.target,
            project,
            args.spider,
            username=args.username,
            password=args.password,
        )
        for spider in _spiders:
            job_id = lib.schedule(
                args.target,
                project,
                spider,
                job_args,
                username=args.username,
                password=args.password,
            )
            print(f"{project} / {spider} => {job_id}")


def spiders(args):
    """List all spiders for the given project(s)."""
    for project in lib.get_projects(args.target, args.project, username=args.username, password=args.password):
        project_spiders = lib.get_spiders(args.target, project, username=args.username, password=args.password)
        if not args.verbose:
            print(f"{project}:")
            if project_spiders:
                print(indent("\n".join(project_spiders), INDENT_PREFIX))
            else:
                print(f"{INDENT_PREFIX}No spiders.")
        elif project_spiders:
            print("\n".join(f"{project} {x}" for x in project_spiders))


def parse_cli_args(args):
    cfg = get_config()

    target_default = cfg.get("deploy", "url", fallback=DEFAULT_TARGET_URL).rstrip("/")
    username_default = cfg.get("deploy", "username", fallback=None)
    password_default = cfg.get("deploy", "password", fallback=None)
    project_default = cfg.get("deploy", "project", fallback=None)
    project_kwargs = {
        "metavar": "PROJECT",
        "required": True,
        "help": "Specifies the project, can be a globbing pattern.",
    }
    if project_default:
        project_kwargs["default"] = project_default

    description = "A command line interface for Scrapyd."
    mainparser = ArgumentParser(description=description)
    subparsers = mainparser.add_subparsers()
    mainparser.add_argument(
        "-t",
        "--target",
        default=target_default,
        help="Specifies the Scrapyd's API base URL.",
    )
    mainparser.add_argument(
        "-u",
        "--username",
        default=username_default,
        help="Specifies the username to connect to the Scrapyd target.",
    )
    mainparser.add_argument(
        "-p",
        "--password",
        default=password_default,
        help="Specifies the password to connect to the Scrapyd target.",
    )

    parser = subparsers.add_parser("deploy", description=deploy.__doc__)
    parser.set_defaults(action=deploy)

    parser = subparsers.add_parser("projects", description=projects.__doc__)
    parser.set_defaults(action=projects)

    parser = subparsers.add_parser("schedule", description=schedule.__doc__)
    parser.set_defaults(action=schedule)
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
