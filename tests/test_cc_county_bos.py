from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.cc_county_bos import CcCountyBosSpider

test_response = file_response(
    join(dirname(__file__), "files", "cc_county_bos.html"),
    url="http://64.166.146.245/agenda_publish.cfm?id=&mt=ALL&get_month=7&get_year=2022",
)
spider = CcCountyBosSpider()

freezer = freeze_time("2022-07-22")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "BOARD OF SUPERVISORS"
    assert parsed_items[11]["title"] == "BOARD OF SUPERVISORS"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 8, 16, 0, 0)
    assert parsed_items[11]["start"] == datetime(2022, 7, 12, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[11]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[11]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "cc_county_bos/202208160000/x/board_of_supervisors"
    assert parsed_items[11]["id"] == "cc_county_bos/202207120000/x/board_of_supervisors"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[11]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "1025 Escobar Street, Martinez, CA 94553",
    }


def test_source():
    assert parsed_items[0]["source"] == (
        "http://64.166.146.245/agenda_publish.cfm"
        "?id=&mt=ALL&get_month=7&get_year=2022"
    )


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[11]["links"] == [
        {
            "href": "http://64.166.146.245/agenda_publish.cfm"
            "?id=&mt=ALL&get_month=7&get_year=2022&dsp=ag&seq=1991",
            "title": "Meeting/Agenda Information",
        },
        {
            "href": "http://64.166.146.245/agenda_publish.cfm"
            "?id=&mt=ALL&get_month=7&get_year=2022&dsp=min&seq=1981",
            "title": "Minutes",
        },
        {
            "href": "http://contra-costa.granicus.com/MediaPlayer.php"
            "?publish_id=6e70c57a-03b8-11ed-baa3-0050569183fa",
            "title": "Video Link",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD
    assert parsed_items[11]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
