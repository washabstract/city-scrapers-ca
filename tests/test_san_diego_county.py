import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.san_diego_county import (
    SanDiegoCountyLegSpider,
    SanDiegoCountySpider,
)

freezer = freeze_time("2022-09-15")
freezer.start()

with open(
    join(dirname(__file__), "files", "san_diego_county.json"), "r", encoding="utf-8"
) as f:
    test_response_leg = json.load(f)

test_response = file_response(
    join(dirname(__file__), "files", "san_diego_county.html"),
    url="https://sdcounty.granicus.com/ViewPublisher.php?view_id=9",
)

spider_leg = SanDiegoCountyLegSpider()
parsed_items = [item for item in spider_leg.parse_legistar(test_response_leg)]

spider = SanDiegoCountySpider()
parsed_items = parsed_items + [item for item in spider.parse(test_response)]


def test_title():
    assert parsed_items[0]["title"] == "Board Of Supervisors"
    assert parsed_items[2]["title"] == "Board of Supervisors Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[2]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 27, 9, 0)
    assert parsed_items[2]["start"] == datetime(2022, 9, 14, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[2]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[2]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "san_diego_county_leg/202209270900/x/board_of_supervisors"
    )
    assert (
        parsed_items[2]["id"]
        == "san_diego_county/202209140000/x/board_of_supervisors_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[2]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "County Administration Center, Room 310",
        "address": "1600 Pacific Highway, San Diego, CA 92101",
    }
    assert parsed_items[2]["location"] == {
        "name": "County Administration Center",
        "address": "1600 Pacific Highway, San Diego, CA 92101",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://sdcounty.legistar.com/Calendar.aspx"
    assert (
        parsed_items[2]["source"]
        == "https://sdcounty.granicus.com/ViewPublisher.php?view_id=9"
    )


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[2]["links"] == [
        {
            "href": "https://sdcounty.granicus.com/AgendaViewer.php?view_id=9&"
            "clip_id=3312",
            "title": "Agenda",
        },
        {
            "href": "https://sdcounty.granicus.com/MediaPlayer.php?view_id=9&"
            "clip_id=3312",
            "title": "Video",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[2]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
