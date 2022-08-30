from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.ladwp import LadwpSpider

test_response = file_response(
    join(dirname(__file__), "files", "ladwp.html"),
    url="http://ladwp.granicus.com/ViewPublisher.php?view_id=2",
)
spider = LadwpSpider()


@pytest.fixture()
def parsed_items():
    freezer = freeze_time("2022-02-18")
    freezer.start()
    parsed_items = [item for item in spider.parse(test_response)]

    # Reading in binary mode
    url_follow_response_2 = file_response(
        join("tests", "files", "ladwp_2.pdf"), mode="rb", url=parsed_items[2].url
    )

    url_follow_response_3 = file_response(
        join("tests", "files", "ladwp_3.pdf"), mode="rb", url=parsed_items[3].url
    )

    parsed_items[2] = next(
        spider._parse_time(
            url_follow_response_2,
            parsed_items[2].cb_kwargs["meeting"],
            parsed_items[2].cb_kwargs["item"],
        )
    )

    parsed_items[3] = next(
        spider._parse_time(
            url_follow_response_3,
            parsed_items[3].cb_kwargs["meeting"],
            parsed_items[3].cb_kwargs["item"],
        )
    )

    freezer.stop()
    return parsed_items


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Board of Commissioners Meeting"
    assert parsed_items[2]["title"] == "Board of Commissioners Meeting"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""
    assert parsed_items[2]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2022, 2, 22, 10, 0)
    assert parsed_items[2]["start"] == datetime(2022, 1, 25, 10, 0)
    assert parsed_items[3]["start"] == datetime(2022, 1, 11, 10, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None
    assert parsed_items[2]["end"] == datetime(2022, 1, 25, 11, 25)
    assert parsed_items[3]["end"] == datetime(2022, 1, 11, 11, 45)


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[2]["time_notes"] == ""


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"] == "ladwp/202202221000/x/board_of_commissioners_meeting"
    )
    assert (
        parsed_items[2]["id"] == "ladwp/202201251000/x/board_of_commissioners_meeting"
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "tentative"
    assert parsed_items[2]["status"] == "passed"


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "address": "",
        "name": "",
    }
    assert parsed_items[2]["location"] == {
        "address": "",
        "name": "",
    }


def test_source(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "http://ladwp.granicus.com/ViewPublisher.php?view_id=2"
    )
    assert (
        parsed_items[2]["source"]
        == "http://ladwp.granicus.com/ViewPublisher.php?view_id=2"
    )


def test_links(parsed_items):
    assert parsed_items[0]["links"] == []
    assert parsed_items[2]["links"] == [
        {
            "href": "https://ladwp.granicus.com/AgendaViewer.php?"
            "view_id=2&clip_id=1871",
            "title": "Board Agenda",
        },
        {
            "href": "https://ladwp.granicus.com/MediaPlayer.php?view_id=2&clip_id=1871",
            "title": "Video",
        },
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[2]["classification"] == BOARD

@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    if type(item) is Meeting:
        assert parsed_items[0]["all_day"] is False
