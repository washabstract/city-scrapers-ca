from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.la_port import LaPortSpider

test_response = file_response(
    join(dirname(__file__), "files", "la_port.html"),
    url = "https://portofla.granicus.com/ViewPublisher.php?view_id=9",
)
spider = LaPortSpider()

freezer = freeze_time("2022-01-25")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

def test_items():
    assert len(parsed_items) > 0

def test_title():
    assert parsed_items[0]["title"] == "Regular Board Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


def test_start():
    assert parsed_items[0]["start"] == datetime(2020, 4, 20, 0, 0)


# def test_end():
#     assert parsed_items[0]["end"] == datetime(2019, 1, 1, 0, 0)


# def test_time_notes():
#     assert parsed_items[0]["time_notes"] == "EXPECTED TIME NOTES"


# def test_id():
#     assert parsed_items[0]["id"] == "EXPECTED ID"


# def test_status():
#     assert parsed_items[0]["status"] == "EXPECTED STATUS"


# def test_location():
#     assert parsed_items[0]["location"] == {
#         "name": "EXPECTED NAME",
#         "address": "EXPECTED ADDRESS"
#     }


# def test_source():
#     assert parsed_items[0]["source"] == "EXPECTED URL"


# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]



# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
