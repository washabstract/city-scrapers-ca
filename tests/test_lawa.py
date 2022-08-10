from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.lawa import LawaSpider

test_response = file_response(
    join(dirname(__file__), "files", "lawa.html"),
    url="http://lawa.granicus.com/ViewPublisher.php?view_id=4",
)
spider = LawaSpider()


@pytest.fixture()
def parsed_items():
    freezer = freeze_time("2022-03-07")
    freezer.start()
    parsed_items = [item for item in spider.parse(test_response)]

    url_follow_response_0 = file_response(
        join("tests", "files", "lawa_0.html"), url=parsed_items[0].url
    )

    url_follow_response_3 = file_response(
        join("tests", "files", "lawa_3.html"), url=parsed_items[0].url
    )

    # Following the first 2 items
    parsed_items[0] = next(
        spider._parse_time(
            url_follow_response_0,
            parsed_items[0].cb_kwargs["meeting"],
            parsed_items[0].cb_kwargs["item"],
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
    assert parsed_items[0]["title"] == "Regular Meeting"
    assert parsed_items[3]["title"] == "Audit Committee Special Meeting"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""
    assert parsed_items[3]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2022, 3, 3, 10, 0)
    assert parsed_items[3]["start"] == datetime(2022, 1, 27, 14, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None
    assert parsed_items[3]["end"] is None


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""


def test_id(parsed_items):
    assert parsed_items[0]["id"] == "lawa/202203031000/x/regular_meeting"
    assert (
        parsed_items[3]["id"] == "lawa/202201271400/x/audit_committee_special_meeting"
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[3]["status"] == "passed"


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {"name": "", "address": ""}
    assert parsed_items[3]["location"] == {
        "name": "Samuel Greenberg Board Room, Clifton A. Moore Administration Building",
        "address": "Los Angeles International Airport, 1 World Way, "
        "Los Angeles, CA 90045",
    }


def test_source(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "http://lawa.granicus.com/ViewPublisher.php?view_id=4"
    )
    assert (
        parsed_items[3]["source"]
        == "http://lawa.granicus.com/ViewPublisher.php?view_id=4"
    )


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {
            "href": "http://lawa.granicus.com/AgendaViewer.php?view_id=4&clip_id=838",
            "title": "Agenda",
        },
        {
            "href": "http://lawa.granicus.com/MediaPlayer.php?view_id=4&clip_id=838",
            "title": "Video",
        },
        {
            "href": "http://lawa.granicus.com/ASX.php?view_id=4&clip_id=838&sn="
            "lawa.granicus.com",
            "title": "Open Video Only in Windows Media Player",
        },
        {
            "href": "http://archive-media.granicus.com:443/OnDemand/lawa/"
            "lawa_84b256f4-2683-46e5-8aa0-7b678a6b79c7.mp4",
            "title": "MP4 Video",
        },
    ]

    assert parsed_items[3]["links"] == [
        {
            "href": "http://lawa.granicus.com/AgendaViewer.php?view_id=4&clip_id=825",
            "title": "Agenda",
        },
        {
            "href": "http://lawa.granicus.com/MediaPlayer.php?view_id=4&clip_id=825",
            "title": "Video",
        },
        {
            "href": "http://lawa.granicus.com/ASX.php?view_id=4&clip_id=825&sn="
            "lawa.granicus.com",
            "title": "Open Video Only in Windows Media Player",
        },
        {
            "href": "http://archive-media.granicus.com:443/OnDemand/lawa/"
            "lawa_3293c1de-0091-4b7c-9181-456315db76e6.mp4",
            "title": "MP4 Video",
        },
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[3]["classification"] == COMMITTEE


def test_all_day(parsed_items):
    if type(parsed_items[0]) is Meeting:
        assert parsed_items[0]["all_day"] is False
