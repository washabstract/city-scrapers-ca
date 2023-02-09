from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.la_county_bos import LaCountyBosSpider

test_response = file_response(
    join(dirname(__file__), "files", "la_county_bos.html"),
    url="http://bos.lacounty.gov/Board-Meeting/Board-Agendas",
)
spider = LaCountyBosSpider()

freezer = freeze_time("2023-02-09")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_items():
    assert len(parsed_items) == 10


def test_title():
    assert parsed_items[0]["title"] == "Public Hearing and Closed Session Meeting"
    assert parsed_items[1]["title"] == "Regular Board Meeting"
    assert parsed_items[2]["title"] == "Public Hearing and Closed Session Meeting"


@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2023, 2, 14, 9, 30)
    assert parsed_items[1]["start"] == datetime(2023, 2, 7, 9, 30)
    assert parsed_items[2]["start"] == datetime(2023, 1, 31, 9, 30)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] is None
    assert parsed_items[2]["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "la_county_bos/202302140930/x/public_hearing_and_closed_session_meeting"
    )
    assert parsed_items[1]["id"] == "la_county_bos/202302070930/x/regular_board_meeting"
    assert (
        parsed_items[2]["id"]
        == "la_county_bos/202301310930/x/public_hearing_and_closed_session_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"
    assert parsed_items[1]["status"] == "passed"
    assert parsed_items[2]["status"] == "passed"


@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "address": "500 West Temple Street, Los Angeles, California 90012",
        "name": "Kenneth Hahn Hall of Administration",
    }


@pytest.mark.parametrize("item", parsed_items)
def test_source(item):
    assert item["source"] == "http://bos.lacounty.gov/Board-Meeting/Board-Agendas"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": (
                "https://assets-us-01.kc-usercontent.com:443/"
                "0234f496-d2b7-00b6-17a4-b43e949b70a2/"
                "b2d11983-ac05-42bd-b367-b3227f68fa4d/"
                "021423_Public%20Hearing%20and%20Closed%20Meeting.pdf"
            ),
            "title": "Agenda",
        },
    ]
    assert parsed_items[1]["links"] == [
        {
            "href": (
                "https://assets-us-01.kc-usercontent.com:443/"
                "0234f496-d2b7-00b6-17a4-b43e949b70a2/"
                "22ebcc07-9176-4fd0-a713-0fd8653fb162/Agenda%20020723_links.pdf"
            ),
            "title": "Agenda",
        },
        {
            "href": (
                "https://assets-us-01.kc-usercontent.com:443/"
                "0234f496-d2b7-00b6-17a4-b43e949b70a2/"
                "e92d566a-8ea1-446a-90bf-a484380af09e/020723.pdf"
            ),
            "title": "Supplemental",
        },
    ]
    assert parsed_items[2]["links"] == [
        {
            "href": (
                "https://assets-us-01.kc-usercontent.com:443/"
                "0234f496-d2b7-00b6-17a4-b43e949b70a2/"
                "6bd6f6d3-4290-4825-82ac-2caaea6f027b/Agenda%20013123_links.pdf"
            ),
            "title": "Agenda",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
