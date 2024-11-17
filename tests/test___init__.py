"""Unit tests for the py_netgear_plus __init__ module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from py_netgear_plus import (
    DEFAULT_PAGE,
    NetgearSwitchConnector,
    _from_bytes_to_megabytes,
    requests,
)
from py_netgear_plus.models import GS308EP, GS316EPP, AutodetectedSwitchModel, GS108Ev3
from py_netgear_plus.netgear_crypt import make_md5, merge

# List of models with saved pages and extracted rand values
FULLY_TESTED_MODELS = [
    (GS108Ev3, "1763184457", "<html></html>"),
    (GS308EP, "990464497", "<html></html>"),
    (GS316EPP, "1127757600", '<html><input name="Gambit" value="cookie_value"</html>'),
]
PARTIALLY_TESTED_MODELS = [
    pytest.param(GS108Ev3, marks=pytest.mark.xfail(reason="no valid data pages")),
    GS308EP,
    GS316EPP,
]

TEST_MODELS = [model[0] for model in FULLY_TESTED_MODELS]


class PageFetcher:
    """A class to fetch pages from a file."""

    def __init__(self, switch_model: type[AutodetectedSwitchModel]) -> None:
        """Initialize the PageFetcher."""
        self.switch_model = switch_model
        self._sequence = 0

    def next_sequence(self) -> int:
        """Get the next sequence number."""
        self._sequence += 1
        return self._sequence

    def from_file(
        self,
        templates: list[dict[str, str]],
        client_hash: str = "",  # noqa: ARG002
    ) -> requests.Response:
        """Fetch a page from a file."""
        response = Mock()
        response.status_code = requests.codes.ok
        response.content = self.get_path(templates).read_bytes()
        return response

    def get_path(self, templates: list[dict[str, str]]) -> Path:
        """Get the path to the first page that exists as a file."""
        for template in templates:
            url = template["url"]
            page_name = url.split("/")[-1] or DEFAULT_PAGE
            path = Path(
                f"pages/{self.switch_model.MODEL_NAME}/{self._sequence}/{page_name}"
            )
            if path.exists():
                return path
        raise FileNotFoundError


def test_0_from_bytes_to_megabytes() -> None:
    """Test cases for _from_bytes_to_megabytes function."""
    assert _from_bytes_to_megabytes(1000000) == 1.00
    assert _from_bytes_to_megabytes(5000000) == 5.00
    assert _from_bytes_to_megabytes(123456789) == 123.46
    assert _from_bytes_to_megabytes(0) == 0.00
    assert _from_bytes_to_megabytes(-1000000) == -1.00


def test_0_netgear_switch_connector_initialization() -> None:
    """Test initialization of NetgearSwitchConnector."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    assert connector.host == "192.168.0.1"
    assert connector._password == "password"
    assert connector.switch_model is not None
    assert connector.ports == 0
    assert connector.poe_ports == []
    assert connector._switch_bootloader == "unknown"
    assert connector.sleep_time == 0.25
    assert connector._login_page_response is not None
    assert connector._login_page_form_password == ""
    assert connector.cookie_name is None
    assert connector.cookie_content is None
    assert connector._client_hash == ""
    assert connector._previous_data == {}
    assert connector._loaded_switch_metadata == {}


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_autodetect_model(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test autodetect_model method."""
    page_fetcher = PageFetcher(switch_model)
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.requests.request") as mock_request:
        mock_response = Mock()
        with page_fetcher.get_path(switch_model.AUTODETECT_TEMPLATES).open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        connector.autodetect_model()
        assert connector._login_page_response == mock_response
        assert isinstance(connector.switch_model, switch_model)


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_check_login_url(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test check_login_url method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.requests.get") as mock_get:
        mock_response = Mock()
        page_name = switch_model.LOGIN_TEMPLATE["url"].split("/")[-1] or DEFAULT_PAGE
        with Path(f"pages/{switch_model.MODEL_NAME}/0/{page_name}").open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_get.return_value = mock_response
        assert connector.check_login_url() is True
        assert connector._login_page_response == mock_response


@pytest.mark.parametrize(
    ("switch_model", "rand", "content"),
    FULLY_TESTED_MODELS,
)
def test_check_login_form_rand(
    switch_model: AutodetectedSwitchModel,
    rand: str,
    content: str,  # noqa: ARG001
) -> None:
    """Test check_login_form_rand method."""
    password = "Password1"
    connector = NetgearSwitchConnector(host="192.168.0.1", password=password)
    connector._login_page_response = Mock()
    page_name = switch_model.LOGIN_TEMPLATE["url"].split("/")[-1] or DEFAULT_PAGE
    with Path(f"pages/{switch_model.MODEL_NAME}/0/{page_name}").open() as file:
        connector._login_page_response.content = file.read()
    connector._login_page_response.status_code = requests.codes.ok
    assert connector.check_login_form_rand() is True
    assert connector._rand == rand
    assert connector._login_page_form_password == make_md5(merge(password, rand))


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_get_unique_id(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test get_unique_id method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector.switch_model = switch_model
    assert (
        connector.get_unique_id()
        == f"{connector.switch_model.__name__.lower()}_192_168_0_1"
    )


@pytest.mark.parametrize(
    ("switch_model", "rand", "content"),
    FULLY_TESTED_MODELS,
)
def test_get_login_password(
    switch_model: type[AutodetectedSwitchModel],
    rand: str,
    content: str,  # noqa: ARG001
) -> None:
    """Test get_login_password method."""
    password = "Password1"
    connector = NetgearSwitchConnector(host="192.168.0.1", password=password)
    with patch("py_netgear_plus.requests.get") as mock_get:
        mock_response = Mock()
        page_name = switch_model.LOGIN_TEMPLATE["url"].split("/")[-1] or DEFAULT_PAGE
        with Path(f"pages/{switch_model.MODEL_NAME}/0/{page_name}").open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_get.return_value = mock_response
        connector._login_page_response = mock_response
        assert connector.get_login_password() == make_md5(merge(password, rand))


@pytest.mark.parametrize(
    ("switch_model", "rand", "content"),
    FULLY_TESTED_MODELS,
)
def test_get_login_cookie_by_model(
    switch_model: AutodetectedSwitchModel, rand: str, content: str
) -> None:
    """Test get_login_cookie method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector.turn_on_offline_mode(f"pages/{switch_model.MODEL_NAME}/0")
    connector.autodetect_model()
    data = {
        connector.switch_model.LOGIN_TEMPLATE["key"]: make_md5(
            merge(connector._password, rand)
        ),
    }
    with (
        patch("py_netgear_plus.requests.request") as mock_request,
    ):
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_response.content = content
        mock_response.cookies.get.return_value = "cookie_value"
        mock_request.return_value = mock_response
        assert connector.get_login_cookie() is True
        mock_request.assert_called()
        mock_request.assert_called_with(
            connector.switch_model.LOGIN_TEMPLATE["method"],
            connector.switch_model.LOGIN_TEMPLATE["url"].format(ip=connector.host),
            data=data,
            allow_redirects=True,
            timeout=connector.LOGIN_URL_REQUEST_TIMEOUT,
        )
        assert connector.cookie_name is not None
        assert connector.cookie_content == "cookie_value"


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        ("GS108Ev3/0/index.htm", True),
        ("GS308EP/unauthenticated.html", False),
        ("GS308EP/0/dashboard.cgi", True),
        ("GS308EP/0/portStatistics.cgi", True),
        ("GS316EPP/unauthenticated.html", False),
        ("GS316EPP/0/dashboard.html", True),
    ],
)
def test_is_authenticated(page: str, expected: bool) -> None:  # noqa: FBT001
    """Test is_authenticated method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="XXXXXXXX")
    response = Mock()
    response.content = Path(f"pages/{page}").read_text()
    response.status_code = requests.codes.ok
    assert connector._is_authenticated(response) is expected


@pytest.mark.parametrize(
    "switch_model",
    PARTIALLY_TESTED_MODELS,
)
def test_get_switch_infos(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test initialization of NetgearSwitchConnector."""
    with (
        patch("py_netgear_plus.time.perf_counter", return_value=0),
        patch("py_netgear_plus.NetgearSwitchConnector.fetch_page") as mock_fetch_page,
    ):
        page_fetcher = PageFetcher(switch_model)
        mock_fetch_page.side_effect = page_fetcher.from_file
        connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
        with patch("py_netgear_plus.requests.request") as mock_request:
            mock_response = Mock()
            with page_fetcher.get_path(
                switch_model.AUTODETECT_TEMPLATES
            ).open() as file:
                mock_response.content = file.read()
            mock_response.status_code = requests.codes.ok
            mock_request.return_value = mock_response
            connector.autodetect_model()
        assert isinstance(connector.switch_model, switch_model)
        connector._login_page_response = Mock()
        with page_fetcher.get_path([switch_model.LOGIN_TEMPLATE]).open() as file:
            connector._login_page_response.content = file.read()
        for sequence in range(2):
            connector._login_page_response.status_code = requests.codes.ok
            switch_data = connector.get_switch_infos()
            with Path(
                f"pages/{switch_model.MODEL_NAME}/{sequence}/switch_infos.json"
            ).open() as file:
                validation_data = json.loads(file.read())
                assert switch_data == validation_data
            page_fetcher.next_sequence()


if __name__ == "__main__":
    pytest.main()
