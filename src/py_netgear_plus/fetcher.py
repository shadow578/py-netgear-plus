"""HTML page retrieval classes."""

import requests
import requests.cookies


class PageNotLoadedError(Exception):
    """Failed to load the page."""


class BaseResponse:
    """Base class for response objects."""

    def __init__(self) -> None:
        """Initialize BaseResponse Object."""
        self.status_code = requests.codes.not_found
        self.content = b""
        self.cookies = requests.cookies.RequestsCookieJar()

    def __bool__(self) -> bool:
        """Return True if status code is 200."""
        return self.status_code == requests.codes.ok
