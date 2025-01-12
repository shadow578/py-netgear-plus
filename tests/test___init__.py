"""Unit tests for the py_netgear_plus __init__ module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests
import requests.cookies
from py_netgear_plus import (
    DEFAULT_PAGE,
    NetgearSwitchConnector,
    _from_bytes_to_megabytes,
)
from py_netgear_plus.fetcher import URL_REQUEST_TIMEOUT, BaseResponse
from py_netgear_plus.models import (
    GS308EP,
    GS308EPP,
    GS316EPP,
    AutodetectedSwitchModel,
    GS108Ev3,
)
from py_netgear_plus.netgear_crypt import merge_hash

# List of models with saved pages, extracted rand values and crypted passwords
FULLY_TESTED_MODELS = [
    (GS108Ev3, "1763184457", "c2c905d5d99f592106a378bf709b737a", "<html></html>"),
    (GS308EP, "990464497", "43001294a37a3f2e1f919b64072a1a32", "<html></html>"),
    (GS308EPP, "1425622205", "e65ad5ee60718843afafeaa03bd1ec49", "<html></html>"),
    (
        GS316EPP,
        "1127757600",
        "3c630eb52109743e94ef671e137b3de0",
        '<html><input name="Gambit" value="cookie_value"</html>',
    ),
]
PARTIALLY_TESTED_MODELS = [
    pytest.param(GS108Ev3, marks=pytest.mark.xfail(reason="no valid data pages")),
    GS308EP,
    GS308EPP,
    GS316EPP,
]

TEST_MODELS = [model[0] for model in FULLY_TESTED_MODELS]


class PyTestPageFetcher:
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
    assert connector._page_fetcher is not None
    assert connector._client_hash == ""
    assert connector._previous_data == {}
    assert connector._loaded_switch_metadata == {}


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_autodetect_model(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test autodetect_model method."""
    page_fetcher = PyTestPageFetcher(switch_model)
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
        mock_response = Mock()
        with page_fetcher.get_path(switch_model.AUTODETECT_TEMPLATES).open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        connector.autodetect_model()
        assert isinstance(connector.switch_model, switch_model)


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_check_login_url(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test check_login_url method."""
    page_fetcher = PyTestPageFetcher(switch_model)
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
        mock_response = Mock()
        with page_fetcher.get_path(switch_model.AUTODETECT_TEMPLATES).open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        assert connector._page_fetcher.check_login_url(switch_model) is True
        assert connector._page_fetcher._login_page_response == mock_response
        checks = switch_model.CHECKS_AND_RESULTS
        if True in next(
            (check[1] for check in checks if check[0] == "check_login_form_rand"),
            [False],
        ):
            rand = connector._page_parser.parse_login_form_rand(
                connector._page_fetcher._login_page_response
            )
            assert rand is not None


@pytest.mark.parametrize(
    ("switch_model", "rand", "crypted_password", "content"),
    FULLY_TESTED_MODELS,
)
def test_parse_login_form_rand(
    switch_model: AutodetectedSwitchModel,
    rand: str,
    crypted_password: str,
    content: str,  # noqa: ARG001
) -> None:
    """Test check_login_form_rand method."""
    password = "Password1"
    connector = NetgearSwitchConnector(host="192.168.0.1", password=password)
    connector._page_fetcher._login_page_response = Mock()
    page_name = switch_model.LOGIN_TEMPLATE["url"].split("/")[-1] or DEFAULT_PAGE
    with Path(f"pages/{switch_model.MODEL_NAME}/0/{page_name}").open() as file:
        connector._page_fetcher._login_page_response.content = file.read()
    connector._page_fetcher._login_page_response.status_code = requests.codes.ok
    assert (
        connector._page_parser.parse_login_form_rand(
            connector._page_fetcher._login_page_response
        )
        == rand
    )
    assert merge_hash(password, rand) == crypted_password


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
    ("switch_model", "rand", "crypted_password", "content"),
    FULLY_TESTED_MODELS,
)
def test_get_login_password(
    switch_model: type[AutodetectedSwitchModel],
    rand: str,
    crypted_password: str,
    content: str,  # noqa: ARG001
) -> None:
    """Test get_login_password method."""
    password = "Password1"
    connector = NetgearSwitchConnector(host="192.168.0.1", password=password)
    with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
        mock_response = Mock()
        page_name = switch_model.LOGIN_TEMPLATE["url"].split("/")[-1] or DEFAULT_PAGE
        with Path(f"pages/{switch_model.MODEL_NAME}/0/{page_name}").open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        connector._page_fetcher._login_page_response = mock_response
        assert merge_hash(password, rand) == crypted_password


@pytest.mark.parametrize(
    ("switch_model", "rand", "crypted_password", "content"),
    FULLY_TESTED_MODELS,
)
def test_get_login_cookie(
    switch_model: AutodetectedSwitchModel,
    rand: str,
    crypted_password: str,  # noqa: ARG001
    content: str,
) -> None:
    """Test get_login_cookie method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector.turn_on_offline_mode(f"pages/{switch_model.MODEL_NAME}/0")
    connector.autodetect_model()
    data = {
        connector.switch_model.LOGIN_TEMPLATE["key"]: merge_hash(
            connector._password, rand
        ),
    }
    with (
        patch("py_netgear_plus.fetcher.requests.request") as mock_request,
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
            timeout=URL_REQUEST_TIMEOUT,
        )
        (cookie_name, cookie_value) = connector.get_cookie()
        assert cookie_name is not None
        assert cookie_value == "cookie_value"


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        ("GS108Ev3/0/index.htm", True),
        ("GS308EP/unauthenticated.html", False),
        ("GS308EP/0/dashboard.cgi", True),
        ("GS308EP/0/portStatistics.cgi", True),
        ("GS308EPP/0/dashboard.cgi", True),
        ("GS308EPP/0/portStatistics.cgi", True),
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
    assert connector._page_fetcher._is_authenticated(response) is expected


@pytest.mark.parametrize(
    "switch_model",
    PARTIALLY_TESTED_MODELS,
)
def test_get_switch_infos(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test initialization of NetgearSwitchConnector."""
    with (
        patch("py_netgear_plus.time.perf_counter", return_value=0),
        patch(
            "py_netgear_plus.NetgearSwitchConnector.fetch_page_from_templates"
        ) as mock_fetch_page_from_templates,
    ):
        page_fetcher = PyTestPageFetcher(switch_model)
        mock_fetch_page_from_templates.side_effect = page_fetcher.from_file
        connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
        with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
            mock_response = Mock()
            with page_fetcher.get_path(
                switch_model.AUTODETECT_TEMPLATES
            ).open() as file:
                mock_response.content = file.read()
            mock_response.status_code = requests.codes.ok
            mock_request.return_value = mock_response
            connector.autodetect_model()
        assert isinstance(connector.switch_model, switch_model)
        connector._page_fetcher._login_page_response = Mock()
        with page_fetcher.get_path([switch_model.LOGIN_TEMPLATE]).open() as file:
            connector._page_fetcher._login_page_response.content = file.read()
        for sequence in range(2):
            connector._page_fetcher._login_page_response.status_code = requests.codes.ok
            switch_data = connector.get_switch_infos()
            with Path(
                f"pages/{switch_model.MODEL_NAME}/{sequence}/switch_infos.json"
            ).open() as file:
                validation_data = json.loads(file.read())
                assert switch_data == validation_data
            page_fetcher.next_sequence()


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_turn_on_and_off_poe_port(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test turning on/off power on a PoE port."""
    with (
        patch(
            "py_netgear_plus.NetgearSwitchConnector.fetch_page_from_templates"
        ) as mock_fetch_page_from_templates,
    ):
        page_fetcher = PyTestPageFetcher(switch_model)
        mock_fetch_page_from_templates.side_effect = page_fetcher.from_file

        connector = NetgearSwitchConnector(host="192.168.0.1", password="password")

        with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
            mock_response = Mock()
            with page_fetcher.get_path(
                switch_model.AUTODETECT_TEMPLATES
            ).open() as file:
                mock_response.content = file.read()
            mock_response.status_code = requests.codes.ok
            mock_request.return_value = mock_response
            connector.autodetect_model()
        assert isinstance(connector.switch_model, switch_model)
        assert isinstance(connector.switch_model.POE_PORTS, list)
        if len(connector.switch_model.POE_PORTS) == 0:
            pytest.skip(f"Model {switch_model.MODEL_NAME} has no PoE ports.")

        connector._client_hash = "client_hash"
        connector._gambit = "gambit"
        connector.set_cookie("cookie_name", "cookie_value")

        response = BaseResponse()
        response.status_code = requests.codes.ok
        response.content = b"SUCCESS"
        with patch(
            "py_netgear_plus.fetcher.requests.request",
            return_value=response,
        ) as mock_request:
            cookies = requests.cookies.RequestsCookieJar()
            cookies.set(
                str(connector.get_cookie()[0]),
                str(connector.get_cookie()[1]),
                domain=connector.host,
                path="/",
            )

            mock_request.return_value = response

            for state in ["on", "off"]:
                poe_port = connector.switch_model.POE_PORTS[0]
                data = connector.switch_model.get_switch_poe_port_data(poe_port, state)
                connector._set_data_from_template(
                    connector.switch_model.SWITCH_POE_PORT_TEMPLATES[0], data
                )
                connector.switch_poe_port(poe_port, state)
                mock_request.assert_called()
                mock_request.assert_called_with(
                    connector.switch_model.SWITCH_POE_PORT_TEMPLATES[0]["method"],
                    connector.switch_model.SWITCH_POE_PORT_TEMPLATES[0]["url"].format(
                        ip=connector.host
                    ),
                    data=data,
                    cookies=cookies,
                    timeout=URL_REQUEST_TIMEOUT,
                    allow_redirects=False,
                )


if __name__ == "__main__":
    pytest.main()
