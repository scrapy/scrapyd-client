import sys
from textwrap import indent

from scrapyd_client import lib

INDENT_PREFIX = "  "


def deploy(args):
    """Deploy a Scrapy project to a Scrapyd instance. For help, invoke scrapyd-deploy."""
    from scrapyd_client import deploy

    sys.argv.pop(1)
    deploy.main()


def projects(args):
    """List all projects deployed on a Scrapyd instance."""
    if _projects := lib.get_projects(
        args.target, username=args.username, password=args.password
    ):
        print("\n".join(_projects))


def schedule(args):
    """Schedule the specified spider(s)."""
    job_args = [(x[0], x[1]) for x in (y.split("=", 1) for y in args.arg)]

    for project in lib.get_projects(
        args.target, args.project, username=args.username, password=args.password
    ):
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
    for project in lib.get_projects(
        args.target, args.project, username=args.username, password=args.password
    ):
        project_spiders = lib.get_spiders(
            args.target, project, username=args.username, password=args.password
        )
        if not args.verbose:
            print(f"{project}:")
            if project_spiders:
                print(indent("\n".join(project_spiders), INDENT_PREFIX))
            else:
                print(f"{INDENT_PREFIX}No spiders.")
        elif project_spiders:
            print("\n".join(f"{project} {x}" for x in project_spiders))
