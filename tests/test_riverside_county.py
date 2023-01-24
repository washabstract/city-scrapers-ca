from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, NOT_CLASSIFIED, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.riverside_county import RiversideCountySpider

start_url = "https://riversidecountyca.iqm2.com/Citizens/calendar.aspx"
test_response = file_response(
    join(dirname(__file__), "files", "riverside_county.html"),
    url=start_url,
)
spider = RiversideCountySpider()

freezer = freeze_time("2023-01-9")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Riverside County Planning Commission - Regular Meeting"
    )
    assert (
        parsed_items[1]["title"] == "(RCA) Western Riverside"
        " County Regional Conservation Authority - Regular Meeting"
    )


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2023, 1, 4, 9, 0)
    assert parsed_items[1]["start"] == datetime(2023, 1, 9, 12, 30)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "riverside_county/202301040900/x"
        "/riverside_county_planning_commission_regular_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[1]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "address": "4080 Lemon Street, Riverside, CA 9250",
        "name": "",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://riversidecountyca.iqm2.com"
            "/FileOpen.aspx?Type=14&ID=2776&Inline=True",
            "title": "Agenda",
        },
        {
            "href": "https://riversidecountyca.iqm2.com"
            "/Citizens/SplitView.aspx?Mode=Video&MeetingID=2826&Format=Agenda",
            "title": "Video",
        },
    ]

    assert parsed_items[1]["links"] == [
        {
            "href": "https://riversidecountyca.iqm2.com"
            "/FileOpen.aspx?Type=14&ID=2827&Inline=True",
            "title": "Agenda",
        },
        {
            "href": "https://riversidecountyca.iqm2.com"
            "/Citizens/SplitView.aspx?Mode=Video&MeetingID=2877&Format=Agenda",
            "title": "Video",
        },
    ]

    assert parsed_items[2]["links"] == [
        {
            "href": "https://riversidecountyca.iqm2.com"
            "/FileOpen.aspx?Type=14&ID=2777&Inline=True",
            "title": "Agenda",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION
    assert parsed_items[1]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
