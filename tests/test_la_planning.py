from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.la_planning import LaPlanningSpider

test_response = file_response(
    join(dirname(__file__), "files", "la_planning.html"),
    url="https://planning.lacity.org/dcpapi/meetings/api/all/commissions/2021",
)
spider = LaPlanningSpider()

freezer = freeze_time("2021-10-27")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "North Valley Region Area Planning Commission"


def test_description():
    assert (
        parsed_items[0]["description"]
        == "North Valley Area Planning Commission Agenda package- Canceled"
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 11, 4, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "la_planning/202111040000/x/north_valley_region_area_planning_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == "cancelled"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Area Planning Commission",
        "address": "North Valley Area Planning Commission Agenda Canceled",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://planning.lacity.org/dcpapi/meetings/api/all/commissions/2021"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://planning.lacity.org/dcpapi/meetings/document/70719",
            "title": "Meeting/Agenda Information",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
