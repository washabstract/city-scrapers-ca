import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from freezegun import freeze_time

from city_scrapers.spiders.corona_city import CoronaCitySpider

freezer = freeze_time("2023-01-9")
freezer.start()

with open(
    join(dirname(__file__), "files", "city_corona.json"), "r", encoding="utf-8"
) as f:
    test_response = json.load(f)

spider = CoronaCitySpider()
parsed_items = [item for item in spider.parse_legistar(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Planning and Housing Commission"
    assert parsed_items[2]["title"] == "Study Session"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2023, 1, 23, 18, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "corona_city/202301231800/x/planning_and_housing_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "400 S. Vicentia Ave. Corona, CA 92882",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "https://corona.legistar.com"
        "/DepartmentDetail.aspx?ID=34213&GUID=A89A630B-E46F-4B71-A423-7C18674BAE62"
    )


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[3]["links"] == [
        {
            "href": "https://corona.legistar.com"
            "/View.ashx?M=A&ID=1073646&GUID=F424643B-3BF1-4CFD-AD59-415BFBD4587A",
            "title": "Agenda",
        },
        {
            "href": "https://corona.legistar.com"
            "/Video.aspx?Mode=Granicus&ID1=1066&Mode2=Video",
            "title": "Video",
        },
        {
            "href": "https://corona.legistar.com"
            "/MeetingDetail.aspx?ID=1073646&GUID="
            "F424643B-3BF1-4CFD-AD59-415BFBD4587A&Options=info|&Search=",
            "title": "Meeting Details",
        },
        {
            "href": "https://corona.legistar.com"
            "/View.ashx?M=PA&ID=1073646&GUID=F424643B-3BF1-4CFD-AD59-415BFBD4587A",
            "title": "Agenda Packet",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
