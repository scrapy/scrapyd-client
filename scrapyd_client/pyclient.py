from __future__ import annotations

from scrapyd_client import lib
from scrapyd_client.utils import DEFAULT_TARGET_URL


class ScrapydClient:
    """ScrapydClient to interact with a Scrapyd instance."""

    def __init__(
        self, url: str = DEFAULT_TARGET_URL, username: str | None = None, password: str | None = None
    ) -> None:
        """Initialize ScrapydClient."""
        self.url = url
        self.username = username
        self.password = password

    def projects(self, pattern: str = "*") -> list[str]:
        return lib.get_projects(
            url=self.url,
            pattern=pattern,
            username=self.username,
            password=self.password,
        )

    def spiders(self, project: str, pattern: str = "*") -> list[str]:
        return lib.get_spiders(
            url=self.url,
            project=project,
            pattern=pattern,
            username=self.username,
            password=self.password,
        )

    def jobs(self, project: str) -> dict:
        return lib.get_jobs(
            url=self.url,
            project=project,
            username=self.username,
            password=self.password,
        )

    def schedule(self, project: str, spider: str, args: list[tuple[str, str]] | None = None) -> str:
        if args is None:
            args = []
        return lib.schedule(
            url=self.url,
            project=project,
            spider=spider,
            args=args,
            username=self.username,
            password=self.password,
        )
