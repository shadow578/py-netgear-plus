"""Definitions of html parsers for Netgear Plus switches."""

import logging
from typing import Any

import requests
from lxml import html

from .fetcher import BaseResponse

_LOGGER = logging.getLogger(__name__)

API_V2_CHECKS = {
    "bootloader": ["V1.00.03", "V2.06.01", "V2.06.02", "V2.06.03"],
    "firmware": ["V2.06.24GR", "V2.06.24EN"],
}


def create_page_parser(switch_model: str) -> Any:
    """Return the parser for the switch model."""
    if switch_model not in PARSERS:
        message = f"Model {switch_model} not supported by the parser."
        raise NetgearPlusPageParserModelNotSupportedError(message)
    return PARSERS[switch_model]()


def get_first_text(tree: html.HtmlElement, xpath: str) -> str:
    """Get the first text from an xpath."""
    try:
        return tree.xpath(xpath)[0].text
    except IndexError as error:
        message = f"XPath {xpath} not found."
        raise NetgearPlusPageParserError(message) from error


def get_first_value(tree: html.HtmlElement, xpath: str) -> str:
    """Get the first value from an xpath."""
    try:
        return tree.xpath(xpath)[0].value
    except IndexError as error:
        message = f"XPath {xpath} not found."
        raise NetgearPlusPageParserError(message) from error


def get_text_from_next_parent_element(tree: html.HtmlElement, xpath: str) -> str:
    """Get the first text from an xpath."""
    try:
        return tree.xpath(xpath)[0].getparent().getnext().text_content()
    except IndexError as error:
        message = f"XPath {xpath} not found."
        raise NetgearPlusPageParserError(message) from error


def get_text_from_next_element(tree: html.HtmlElement, xpath: str) -> str:
    """Get the first text from an xpath."""
    try:
        return tree.xpath(xpath)[0].getnext().text_content()
    except IndexError as error:
        message = f"XPath {xpath} not found."
        raise NetgearPlusPageParserError(message) from error


class NetgearPlusPageParserError(Exception):
    """Base class for NetgearSwitchParser errors."""


class NetgearPlusPageParserModelNotSupportedError(NetgearPlusPageParserError):
    """Model not supported by the parser."""


class PageParser:
    """Base class for parsing Netgear Plus html pages."""

    def __init__(self) -> None:
        """Empty contructor."""
        self._switch_firmware = None
        self._switch_bootloader = None
        self._port_status = {}
        _LOGGER.debug("%s(PageParser) object initialized.", self.__class__.__name__)

    def has_api_v2(self) -> bool:
        """Check if the switch has API v2."""
        if not self._switch_firmware or not self._switch_bootloader:
            error_message = "Firmware or bootloader version not set."
            raise NetgearPlusPageParserError(error_message)
        match_bootloader = self._switch_bootloader in API_V2_CHECKS["bootloader"]
        match_firmware = self._switch_firmware in API_V2_CHECKS["firmware"]
        return match_bootloader and match_firmware

    def parse_switch_metadata(
        self, page: requests.Response | BaseResponse
    ) -> dict[str, Any]:
        """Parse switch info from the html page."""
        tree = html.fromstring(page.content)

        switch_name = get_first_value(tree, '//input[@id="switch_name"]')
        switch_serial_number = get_first_text(tree, '//table[@id="tbl1"]/tr[3]/td[2]')

        # Detect Firmware (2nd xpath is for older firmware)
        self._switch_firmware = get_first_text(
            tree, '//table[@id="tbl1"]/tr[6]/td[2]'
        ) or get_first_text(tree, '//table[@id="tbl1"]/tr[4]/td[2]')

        self._switch_bootloader = get_first_text(tree, '//td[@id="loader"]')

        return {
            "switch_name": switch_name,
            "switch_serial_number": switch_serial_number,
            "switch_bootloader": self._switch_bootloader,
            "switch_firmware": self._switch_firmware,
        }

    def parse_client_hash(self, page: requests.Response | BaseResponse) -> str | None:
        """Parse the client hash from the html page."""
        tree = html.fromstring(page.content)
        return get_first_value(tree, '//input[@name="hash"]')

    def parse_port_status(
        self, page: requests.Response | BaseResponse, ports: int
    ) -> dict[int, dict[str, Any]]:
        """Parse port status from the html page."""
        status_by_port = {}

        if self.has_api_v2():
            tree = html.fromstring(page.content)
            _port_elems = tree.xpath('//tr[@class="portID"]/td[2]')
            portstatus_elems = tree.xpath('//tr[@class="portID"]/td[3]')
            portspeed_elems = tree.xpath('//tr[@class="portID"]/td[4]')
            portconnectionspeed_elems = tree.xpath('//tr[@class="portID"]/td[5]')

            for port_nr in range(ports):
                try:
                    status_text = portstatus_elems[port_nr].text.replace("\n", "")
                    modus_speed_text = portspeed_elems[port_nr].text.replace("\n", "")
                    connection_speed_text = portconnectionspeed_elems[
                        port_nr
                    ].text.replace("\n", "")
                except (IndexError, AttributeError):
                    status_text = self.port_status.get(port_nr + 1, {}).get(
                        "status", None
                    )
                    modus_speed_text = self.port_status.get(port_nr + 1, {}).get(
                        "modus_speed", None
                    )
                    connection_speed_text = self.port_status.get(port_nr + 1, {}).get(
                        "connection_speed", None
                    )
                status_by_port[port_nr + 1] = {
                    "status": status_text,
                    "modus_speed": modus_speed_text,
                    "connection_speed": connection_speed_text,
                }

        self.port_status = status_by_port
        _LOGGER.debug("Port Status is %s", self.port_status)
        return status_by_port

    def parse_port_statistics(
        self, page: requests.Response | BaseResponse
    ) -> dict[str, Any]:
        """Parse port statistics from the html page."""
        if self.has_api_v2():
            return self.parse_port_statistics_v2(page)
        return self.parse_port_statistics_v1(page)

    def parse_port_statistics_v1(
        self, page: requests.Response | BaseResponse
    ) -> dict[str, Any]:
        """Parse port status from the html page."""
        raise NotImplementedError

    def parse_port_statistics_v2(
        self, page: requests.Response | BaseResponse
    ) -> dict[str, Any]:
        """Parse port status from the html page."""
        raise NotImplementedError

    def parse_poe_port_config(
        self, page: requests.Response | BaseResponse
    ) -> dict[str, Any]:
        """Parse PoE port configuration from the html page."""
        raise NotImplementedError


class GS105E(PageParser):
    """Parser for the GS105E switch."""

    def __init__(self) -> None:
        """Initialize the GS105E parser."""
        super().__init__()


class GS105Ev2(PageParser):
    """Parser for the GS105Ev2 switch."""

    def __init__(self) -> None:
        """Initialize the GS105Ev2 parser."""
        super().__init__()


class GS105Ev3(PageParser):
    """Parser for the GS105Ev3 switch."""

    def __init__(self) -> None:
        """Initialize the GS105Ev3 parser."""
        super().__init__()


class GS108E(PageParser):
    """Parser for the GS108E switch."""

    def __init__(self) -> None:
        """Initialize the GS108E parser."""
        super().__init__()


class GS108Ev3(PageParser):
    """Parser for the GS108E v3switch."""

    def __init__(self) -> None:
        """Initialize the GS108E parser."""
        super().__init__()


class GS30xSeries(PageParser):
    """Parser for the GS30x switch series."""

    def __init__(self) -> None:
        """Initialize the GS30xSeries parser."""
        super().__init__()

    def parse_switch_metadata(
        self, page: requests.Response | BaseResponse
    ) -> dict[str, Any]:
        """Parse switch info from the html page."""
        tree = html.fromstring(page.content)

        switch_name = get_first_text(tree, '//div[@id="switch_name"]')
        switch_serial_number = get_text_from_next_parent_element(
            tree, '//span[text()="ml198"]'
        )
        self._switch_bootloader = "unknown"
        self._switch_firmware = get_text_from_next_parent_element(
            tree, '//span[text()="ml089"]'
        )

        return {
            "switch_name": switch_name,
            "switch_serial_number": switch_serial_number,
            "switch_bootloader": self._switch_bootloader,
            "switch_firmware": self._switch_firmware,
        }

    def parse_port_status(
        self, page: requests.Response | BaseResponse, ports: int
    ) -> dict[int, dict[str, Any]]:
        """Parse port status from the html page."""
        tree = html.fromstring(page.content)

        status_by_port = {}
        for port0 in range(ports):
            port_nr = port0 + 1
            xtree_port = tree.xpath(f'//div[@name="isShowPot{port_nr}"]')[0]
            port_state_text = xtree_port[1][0].text

            modus_speed_text = tree.xpath('//input[@class="Speed"]')[port0].value
            if modus_speed_text == "1":
                modus_speed_text = "Auto"
            connection_speed_text = tree.xpath('//input[@class="LinkedSpeed"]')[
                port0
            ].value
            connection_speed_text = (
                connection_speed_text.replace("full", "").replace("half", "").strip()
            )

            status_by_port[port_nr] = {
                "status": port_state_text,
                "modus_speed": modus_speed_text,
                "connection_speed": connection_speed_text,
            }

        self.port_status = status_by_port
        _LOGGER.debug("Port Status is %s", self.port_status)
        return status_by_port


class GS305EP(GS30xSeries):
    """Parser for the GS305EP switch."""

    def __init__(self) -> None:
        """Initialize the GS305EP parser."""
        super().__init__()


class GS308EP(GS30xSeries):
    """Parser for the GS108EP switch."""

    def __init__(self) -> None:
        """Initialize the GS308EP parser."""
        super().__init__()


class GS31xSeries(PageParser):
    """Parser for the GS31x switch series."""

    def __init__(self) -> None:
        """Initialize the GS31xSeries parser."""
        super().__init__()

    def parse_switch_metadata(
        self, page: requests.Response | BaseResponse
    ) -> dict[str, Any]:
        """Parse switch info from the html page."""
        tree = html.fromstring(page.content)

        switch_name = get_first_value(tree, '//input[@name="switchName"]')
        switch_serial_number = get_text_from_next_element(
            tree, '//p[contains(text(),"Serial Number")]'
        )
        self._switch_bootloader = "unknown"
        self._switch_firmware = get_text_from_next_element(
            tree, '//p[contains(text(),"Firmware Version")]'
        )

        return {
            "switch_name": switch_name,
            "switch_serial_number": switch_serial_number,
            "switch_bootloader": self._switch_bootloader,
            "switch_firmware": self._switch_firmware,
        }

    def parse_client_hash(self, page: requests.Response | BaseResponse) -> str | None:  # noqa: ARG002
        """Return None as these switches do not have a hash value."""
        return None

    def parse_port_status(
        self, page: requests.Response | BaseResponse, ports: int
    ) -> dict[int, dict[str, Any]]:
        """Parse port status from the html page."""
        tree = html.fromstring(page.content)
        xtree_port_statusses = tree.xpath('//span[contains(@class,"status-on-port")]')
        xtree_port_attributes = tree.xpath('//div[@class="port-status"]')
        if len(xtree_port_statusses) != ports or len(xtree_port_attributes) != ports:
            message = (
                "Port count mismatch: Expected %s, got %s (status) and %s (attributes)",
                ports,
                len(xtree_port_statusses),
                len(xtree_port_attributes),
            )
            raise NetgearPlusPageParserError(message)
        status_by_port = {}
        for port_nr0 in range(ports):
            port_nr = port_nr0 + 1
            port_state_text = xtree_port_statusses[port_nr0].text
            port_attributes = xtree_port_attributes[port_nr0].xpath("./div/div/p")
            modus_speed_text = port_attributes[1].text
            connection_speed_text = port_attributes[1].text.replace("half", "").strip()

            status_by_port[port_nr] = {
                "status": port_state_text,
                "modus_speed": modus_speed_text,
                "connection_speed": connection_speed_text,
            }

        self.port_status = status_by_port
        _LOGGER.debug("Port Status is %s", self.port_status)
        return status_by_port


class GS316EP(GS31xSeries):
    """Parser for the GS316EP switch."""

    def __init__(self) -> None:
        """Initialize the GS316EP parser."""
        super().__init__()


class GS316EPP(GS31xSeries):
    """Parser for the GS316EPP switch."""

    def __init__(self) -> None:
        """Initialize the GS316EPP parser."""
        super().__init__()


PARSERS = {
    "GS105E": GS105E,
    "GS105Ev2": GS105Ev2,
    "GS105Ev3": GS105Ev3,
    "GS108E": GS108E,
    "GS108Ev3": GS108Ev3,
    "GS305EP": GS305EP,
    "GS308EP": GS308EP,
    "GS316EP": GS316EP,
    "GS316EPP": GS316EPP,
}
