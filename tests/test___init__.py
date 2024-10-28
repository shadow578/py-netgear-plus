"""Unit tests for the netgear_plus __init__ module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from py_netgear_plus import (
    NetgearSwitchConnector,
    _from_bytes_to_megabytes,
    requests,
)
from py_netgear_plus.models import GS308EP


def test_from_bytes_to_megabytes() -> None:
    """Test cases for _from_bytes_to_megabytes function."""
    assert _from_bytes_to_megabytes(1000000) == 1.00
    assert _from_bytes_to_megabytes(5000000) == 5.00
    assert _from_bytes_to_megabytes(123456789) == 123.46
    assert _from_bytes_to_megabytes(0) == 0.00
    assert _from_bytes_to_megabytes(-1000000) == -1.00


"""Unit tests for the netgear_plus __init__ module."""


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
    with patch("netgear_plus.requests.request") as mock_request:
        with Path("tests/GS308EP_login.cgi").open() as file:
            mock_request.content = file.read()  # type: ignore reportAttributeAccessIssue
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        with patch(
            "netgear_plus.models.AutodetectedSwitchModel.AUTODETECT_TEMPLATES",
            new=[{"url": "http://{ip}/", "method": "get"}],
        ) and patch(
            "netgear_plus.models.MODELS",
            new=[
                GS308EP,
            ],
        ):
            connector.autodetect_model()
            assert connector._login_page_response == mock_response


def test_check_login_url() -> None:
    """Test check_login_url method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("netgear_plus.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_get.return_value = mock_response
        assert connector.check_login_url() is True
        assert connector._login_page_response == mock_response


def test_check_login_form_rand() -> None:
    """Test check_login_form_rand method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("netgear_plus.html.fromstring") as mock_fromstring:
        mock_tree = Mock()
        mock_tree.xpath.return_value = [Mock(value="rand_value")]
        mock_fromstring.return_value = mock_tree
        connector._login_page_response.content = b"content"  # type: ignore reportAttributeAccessIssue
        with patch("netgear_plus.netgear_crypt.merge", return_value="merged") and patch(
            "netgear_plus.netgear_crypt.make_md5", return_value="md5_str"
        ):
            assert connector.check_login_form_rand() is True
            assert connector._login_page_form_password == "md5_str"


def test_get_unique_id() -> None:
    """Test get_unique_id method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector.switch_model.MODEL_NAME = "TestModel"  # type: ignore reportAttributeAccessIssue
    assert connector.get_unique_id() == "testmodel_192_168_0_1"


def test_get_login_password() -> None:
    """Test get_login_password method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch.object(connector, "check_login_url", return_value=True) and patch.object(
        connector, "check_login_form_rand", return_value=True
    ):
        assert connector.get_login_password() == "password"


def test_get_login_cookie() -> None:
    """Test get_login_cookie method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector.switch_model = Mock()
    connector.switch_model.LOGIN_TEMPLATE = {
        "url": "http://{ip}/",
        "method": "post",
        "key": "password",
    }
    with patch.object(
        connector, "get_login_password", return_value="password"
    ) and patch("netgear_plus.requests.request") as mock_request:
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_response.cookies.get.return_value = "cookie_value"
        mock_request.return_value = mock_response
        assert connector.get_login_cookie() is True
        assert connector.cookie_name is not None
        assert connector.cookie_content == "cookie_value"


if __name__ == "__main__":
    pytest.main()
