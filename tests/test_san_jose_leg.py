import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE
from freezegun import freeze_time

from city_scrapers.spiders.san_jose_leg import SanJoseLegSpider

freezer = freeze_time("2021-11-01")
freezer.start()

with open(
    join(dirname(__file__), "files", "san_jose_leg.json"), "r", encoding="utf-8"
) as f:
    test_response = json.load(f)

spider = SanJoseLegSpider()
parsed_items = [item for item in spider.parse_legistar(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Transportation and Environment Committee (T&E)"


def test_description():
    assert parsed_items[0]["description"] == (
        "https://sanjose.legistar.com/"
        "MeetingDetail.aspx?ID=897916&GUID=BD24BA79-B34D-42E0-A633-DAFAF6BEA15F"
        "&Options=info|&Search="
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 11, 1, 13, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "san_jose_leg/202111011330/x/transportation_and_environment_committee_t_e_"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Virtual Meeting -  https://sanjoseca.zoom.us/j/95576437230",
        "address": "https://sanjoseca.zoom.us/j/95576437230",
    }


def test_source():
    assert parsed_items[0]["source"] == (
        "https://sanjose.legistar.com/DepartmentDetail.aspx?ID=33885"
        "&GUID=B8D373E4-359D-470B-962C-BFAA26D7ED6E"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://sanjose.legistar.com/View.ashx?M=A&ID=897916"
            "&GUID=BD24BA79-B34D-42E0-A633-DAFAF6BEA15F",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
