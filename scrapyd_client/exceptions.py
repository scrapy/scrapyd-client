class ErrorResponse(Exception):  # noqa: N818
    """Raised when Scrapyd reports an error."""


class MalformedResponse(Exception):  # noqa: N818
    """Raised when the response can't be decoded."""
