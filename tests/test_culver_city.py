import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from freezegun import freeze_time

from city_scrapers.spiders.culver_city import CulverCitySpider

freezer = freeze_time("2022-02-04")
freezer.start()

with open(
    join(dirname(__file__), "files", "culver_city.json"), "r", encoding="utf-8"
) as f:
    test_response = json.load(f)

spider = CulverCitySpider()
parsed_items = [item for item in spider.parse_legistar(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "COMMITTEE ON PERMITS AND LICENSES"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 2, 9, 11, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "culver_city/202202091100/x/committee_on_permits_and_licenses"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Mike Balkman Council Chambers", "address": ""}


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://culver-city.legistar.com/DepartmentDetail.aspx?ID=28558&"
        "GUID=C77AB0A1-4E49-4D20-BFB7-6123510C0D4B"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://culver-city.legistar.com/View.ashx?M=A&ID=930142"
            "&GUID=051FCF61-EDBF-4E7A-A0FF-BE874BF039DF",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
