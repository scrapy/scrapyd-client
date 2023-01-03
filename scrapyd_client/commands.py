import sys

from scrapyd_client import lib
from scrapyd_client.utils import indent

INDENT_PREFIX = "  "


def deploy(args):
    """Deploy a Scrapy project to a Scrapyd instance. For help, invoke scrapyd-deploy."""
    from scrapyd_client import deploy

    sys.argv.pop(1)
    deploy.main()


def projects(args):
    """List all projects deployed on a Scrapyd instance."""
    _projects = lib.get_projects(
        args.target, username=args.username, password=args.password
    )
    if _projects:
        print("\n".join(_projects))


def schedule(args):
    """Schedule the specified spider(s)."""
    job_args = dict((x[0], x[1]) for x in (y.split("=", 1) for y in args.arg))
    _projects = lib.get_projects(
        args.target, args.project, username=args.username, password=args.password
    )
    for project in _projects:
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
    _projects = lib.get_projects(
        args.target, args.project, username=args.username, password=args.password
    )
    for project in _projects:
        project_spiders = lib.get_spiders(
            args.target, project, username=args.username, password=args.password
        )
        if not args.verbose:
            print(f"{project}:")
            if project_spiders:
                print(indent("\n".join(project_spiders), INDENT_PREFIX))
            else:
                print(INDENT_PREFIX + "No spiders.")
        elif project_spiders:
            print("\n".join(f"{project} {x}" for x in project_spiders))
