from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMITTEE, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.south_coast_air_quality_management import (
    SouthCoastAirQualityManagementSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "south_coast_air_quality_management.html"),
    url="http://www.aqmd.gov/home/news-events/meeting-agendas-minutes?filter=All",
)
spider = SouthCoastAirQualityManagementSpider()

freezer = freeze_time("2022-10-10")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Stationary Source"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 10, 21, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "south_coast_air_quality_management/202210210000/x/stationary_source"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "21865 Copley Dr, Diamond Bar, CA 91765",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://www.aqmd.gov/home/news-events/meeting-agendas-minutes?filter=All"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://www.aqmd.gov/home/news-events/meeting-agendas-minutes"
            "/agenda?title=stationary-source-committee-october-21-2022",
            "title": "Agenda",
        }
    ]

    assert parsed_items[0]["links"] == [
        {
            "href": "http://www.aqmd.gov/home/news-events/meeting-agendas-minutes"
            "/agenda?title=stationary-source-committee-october-21-2022",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
