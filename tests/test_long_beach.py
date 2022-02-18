import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from freezegun import freeze_time

from city_scrapers.spiders.long_beach import LongBeachSpider

freezer = freeze_time("2022-02-04")
freezer.start()

with open(
    join(dirname(__file__), "files", "long_beach.json"), "r", encoding="utf-8"
) as f:
    test_response = json.load(f)

spider = LongBeachSpider()
parsed_items = [item for item in spider.parse_legistar(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Economic Development Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 2, 16, 16, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "long_beach/202202161600/x/economic_development_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "411 W. Ocean Boulevard "
        "10th Floor Conference Room VIA TELECONFERENCE",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://longbeach.legistar.com/DepartmentDetail.aspx?ID=2512&"
        "GUID=F050FB58-374F-49BE-8F22-A46417A0CAD3"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://longbeach.legistar.com/View.ashx?M=A&ID=929995&"
            "GUID=A72AC276-1664-492A-A815-2CEE02B847AA",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False