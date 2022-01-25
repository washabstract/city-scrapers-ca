import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from freezegun import freeze_time

from city_scrapers.spiders.la_metro import LaMetroLegSpider

freezer = freeze_time("2022-01-24")
freezer.start()

with open(
    join(dirname(__file__), "files", "la_metro.json"), "r", encoding="utf-8"
) as f:
    test_response = json.load(f)

spider = LaMetroLegSpider()
parsed_items = [item for item in spider.parse_legistar(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board of Directors - Regular Board Meeting"


# Meeting Details
def test_description():
    assert parsed_items[0]["description"] == (
        "https://metro.legistar.com/"
        "MeetingDetail.aspx?ID=878163&GUID=6A797765-BC87-4FAD-9770-472376E81AE1"
        "&Options=info|&Search="
    )


# Meeting Date and Meeting Time
def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 1, 27, 10, 00)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


# name/startime/item_id/underscore_title
def test_id():
    assert (
        parsed_items[0]["id"]
        == "la_metro_leg/202201271000/x/board_of_directors_regular_board_meeting"
    )


# has it been confirmed canceled?
def test_status():
    assert parsed_items[0]["status"] == "tentative"


# Meeting Location
def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Watch online:  http://boardagendas.metro.net \r\nListen by phone: Dial"
        " 888-251-2949 and enter Access Code: \r\n8231160# (English) or 4544724# ("
        "Español) To give written or live public comment, please see the top of page 4",
        "address": "http://boardagendas.metro.net",
    }


# Name URL
def test_source():
    assert parsed_items[0]["source"] == (
        "https://metro.legistar.com/DepartmentDetail.aspx?ID=28529"
        "&GUID=44319A1A-B2B7-48CC-B857-ADCE9064573B"
    )


# Agenda
def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://metro.legistar.com/View.ashx?M=A&ID=878163"
            "&GUID=6A797765-BC87-4FAD-9770-472376E81AE1",
            "title": "Agenda",
        }
    ]


# Name classification
def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
