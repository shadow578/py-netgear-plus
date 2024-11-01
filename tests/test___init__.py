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
from py_netgear_plus.models import GS308EP, AutodetectedSwitchModel, GS3xxSeries


def test_from_bytes_to_megabytes() -> None:
    """Test cases for _from_bytes_to_megabytes function."""
    assert _from_bytes_to_megabytes(1000000) == 1.00
    assert _from_bytes_to_megabytes(5000000) == 5.00
    assert _from_bytes_to_megabytes(123456789) == 123.46
    assert _from_bytes_to_megabytes(0) == 0.00
    assert _from_bytes_to_megabytes(-1000000) == -1.00


"""Unit tests for the py_netgear_plus __init__ module."""


def test_netgear_switch_connector_initialization() -> None:
    """Test initialization of NetgearSwitchConnector."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    assert connector.host == "192.168.0.1"
    assert connector._password == "password"
    assert connector.switch_model is not None
    assert connector.ports == 0
    assert connector.poe_ports == []
    assert connector.port_status == {}
    assert connector._switch_bootloader == "unknown"
    assert connector.sleep_time == 0.25
    assert connector._login_page_response is not None
    assert connector._login_page_form_password == ""
    assert connector.cookie_name is None
    assert connector.cookie_content is None
    assert connector._client_hash == ""
    assert connector._previous_data == {}
    assert connector._loaded_switch_infos == {}


def test_autodetect_model() -> None:
    """Test autodetect_model method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.requests.request") as mock_request:
        mock_response = Mock()
        with Path("pages/GS308EP/login.cgi").open() as file:
            mock_response.content = file.read()  # type: ignore reportAttributeAccessIssue
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        connector.autodetect_model()
        assert connector._login_page_response == mock_response
        assert isinstance(connector.switch_model, GS308EP)


def test_check_login_url() -> None:
    """Test check_login_url method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.requests.get") as mock_get:
        mock_response = Mock()
        with Path("pages/GS308EP/login.cgi").open() as file:
            mock_response.content = file.read()  # type: ignore reportAttributeAccessIssue
        mock_response.status_code = requests.codes.ok
        mock_get.return_value = mock_response
        assert connector.check_login_url() is True
        assert connector._login_page_response == mock_response


def test_check_login_form_rand() -> None:
    """Test check_login_form_rand method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector._login_page_response = Mock()
    with Path("pages/GS308EP/login.cgi").open() as file:
        connector._login_page_response.content = file.read()  # type: ignore reportAttributeAccessIssue
    connector._login_page_response.status_code = requests.codes.ok
    assert connector.check_login_form_rand() is True
    assert connector._login_page_form_password == "53765442b8360ee03c5fd72ff02deced"


def test_get_unique_id() -> None:
    """Test get_unique_id method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector.switch_model.MODEL_NAME = "TestModel"  # type: ignore reportAttributeAccessIssue
    assert connector.get_unique_id() == "testmodel_192_168_0_1"


def test_get_login_password() -> None:
    """Test get_login_password method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.requests.get") as mock_get:
        mock_response = Mock()
        with Path("pages/GS308EP/login.cgi").open() as file:
            mock_response.content = file.read()  # type: ignore reportAttributeAccessIssue
        mock_response.status_code = requests.codes.ok
        mock_get.return_value = mock_response
        connector._login_page_response = mock_response
        assert connector.get_login_password() == "53765442b8360ee03c5fd72ff02deced"


def test_get_login_cookie() -> None:
    """Test get_login_cookie method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector.switch_model = GS308EP  # type: ignore reportAttributeAccessIssue
    with (
        patch.object(connector, "get_login_password", return_value="password"),
        patch("py_netgear_plus.requests.request") as mock_request,
    ):
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_response.cookies.get.return_value = "cookie_value"
        mock_request.return_value = mock_response
        assert connector.get_login_cookie() is True
        assert connector.cookie_name is not None
        assert connector.cookie_content == "cookie_value"


class PageFetcher:
    """A class to fetch pages from a file."""

    def __init__(self, switch_model: AutodetectedSwitchModel) -> None:
        """Initialize the PageFetcher."""
        self.switch_model = switch_model

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
        """Get the path to a page."""
        for template in templates:
            url = template["url"]
            page_name = url.split("/")[-1] or DEFAULT_PAGE
            path = Path(f"pages/{self.switch_model.MODEL_NAME}/{page_name}")
            if path.exists():
                return path
        raise FileNotFoundError


def test_get_switch_infos() -> None:
    """Test initialization of NetgearSwitchConnector."""
    switch_model = GS308EP()
    with (
        patch("py_netgear_plus.time.perf_counter", return_value=0),
        patch("py_netgear_plus.NetgearSwitchConnector.fetch_page") as mock_fetch_page,
    ):
        page_fetcher = PageFetcher(switch_model)  # type: ignore reportAttributeTypeIssue
        mock_fetch_page.side_effect = page_fetcher.from_file
        connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
        with patch("py_netgear_plus.requests.request") as mock_request:
            mock_response = Mock()
            with page_fetcher.get_path(
                switch_model.AUTODETECT_TEMPLATES
            ).open() as file:
                mock_response.content = file.read()  # type: ignore reportAttributeAccessIssue
            mock_response.status_code = requests.codes.ok
            mock_request.return_value = mock_response
            connector.autodetect_model()
        assert isinstance(connector.switch_model, GS3xxSeries)
        connector._login_page_response = Mock()
        with page_fetcher.get_path([switch_model.LOGIN_TEMPLATE]).open() as file:
            connector._login_page_response.content = file.read()  # type: ignore reportAttributeAccessIssue
        connector._login_page_response.status_code = requests.codes.ok
        switch_data = connector.get_switch_infos()
        with Path(f"pages/{switch_model.MODEL_NAME}/switch_infos.json").open() as file:
            validation_data = json.loads(file.read())
            assert switch_data == validation_data


if __name__ == "__main__":
    pytest.main()
