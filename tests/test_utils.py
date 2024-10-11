import netrc

import pytest
from requests.auth import HTTPBasicAuth

from scrapyd_client.utils import get_auth

try:
    netrc.netrc()
    exists = True
except FileNotFoundError:
    exists = False


@pytest.mark.skipif(exists, reason="a .netrc file exists")
@pytest.mark.parametrize(
    ("url", "username", "password", "expected"),
    [
        ("http://localhost:6800", None, None, None),
        (
            "http://localhost:6800",
            "user",
            "pass",
            HTTPBasicAuth("user", "pass"),
        ),
    ],
)
def test_get_auth(url, username, password, expected):
    assert get_auth(url, username, password) == expected


def test_get_auth_netrc(mocker):
    n = mocker.patch("scrapyd_client.utils.netrc")  # mock netrc
    n.netrc.return_value.authenticators.return_value = ("user", "", "pass")
    assert get_auth("http://localhost:6800", None, None) == HTTPBasicAuth("user", "pass")
