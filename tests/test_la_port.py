from datetime import datetime
from os.path import join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.la_port import LaPortSpider

test_response = file_response(
    join("tests", "files", "la_port.html"),
    url="https://portofla.granicus.com/ViewPublisher.php?view_id=9",
)
spider = LaPortSpider()

freezer = freeze_time("2022-01-25")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
test_response_0 = file_response(
    join("tests", "files", "la_port_0.html"), url=parsed_items[0].url
)
parsed_items[0] = next(
    spider._parse_time_location(
        test_response_0,
        parsed_items[0]._cb_kwargs["meeting"],
        parsed_items[0]._cb_kwargs["item"],
    )
)
test_response_24 = file_response(
    join("tests", "files", "la_port_24.html"), url=parsed_items[24].url
)
parsed_items[24] = next(
    spider._parse_time_location(
        test_response_24,
        parsed_items[24]._cb_kwargs["meeting"],
        parsed_items[24]._cb_kwargs["item"],
    )
)
freezer.stop()


def test_items():
    assert len(parsed_items) > 0


def test_title():
    assert parsed_items[0]["title"] == "Regular Board Meeting"
    assert parsed_items[24]["title"] == "Regular Board Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[24]["description"] == ""


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[24]["classification"] == BOARD


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 1, 27, 9, 0)
    assert parsed_items[24]["start"] == datetime(2022, 1, 13, 9, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[24]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[24]["time_notes"] == ""


def test_location():
    name = "Los Angeles Board of Harbor Commissioners"
    address = """Harbor Administration Building\n425 S. Palos Verdes Street
San Pedro, California 90731"""
    location = {"name": name, "address": address}

    assert parsed_items[0]["location"] == location
    assert parsed_items[24]["location"] == location


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://portofla.granicus.com/AgendaViewer.php"
            "?view_id=9&event_id=666",
            "title": "Agenda",
        }
    ]
    assert parsed_items[24]["links"] == [
        {
            "href": "https://portofla.granicus.com/AgendaViewer.php?"
            "view_id=9&clip_id=1624",
            "title": "Agenda",
        },
        {
            "href": "https://portofla.granicus.com/MediaPlayer.php?"
            "view_id=9&clip_id=1624",
            "title": "Audio/Video Recording",
        },
    ]


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://portofla.granicus.com/ViewPublisher.php?view_id=9"
    )
    assert (
        parsed_items[24]["source"]
        == "https://portofla.granicus.com/ViewPublisher.php?view_id=9"
    )


def test_id():
    assert parsed_items[0]["id"] == "la_port/202201270900/x/regular_board_meeting"
    assert parsed_items[24]["id"] == "la_port/202201130900/x/regular_board_meeting"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[24]["status"] == PASSED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    if type(item) is Meeting:
        assert item["all_day"] is False
