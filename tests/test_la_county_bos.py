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

freezer = freeze_time("2021-03-24")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_items():
    assert len(parsed_items) == 4


def test_title():
    assert parsed_items[0]["title"] == "Regular Meeting"
    assert parsed_items[1]["title"] == "Special Meeting"
    assert parsed_items[2]["title"] == "Regular Meeting"
    assert parsed_items[3]["title"] == "Special Closed Session Meeting"


def test_description():
    assert parsed_items[0]["description"] == (
        "Meeting Agenda: "
        "http://bos.lacounty.gov/LinkClick.aspx?fileticket=uubFVO4njSk%3d&portalid=1\n"
        "Supplemental Agenda: "
        "http://bos.lacounty.gov/LinkClick.aspx?fileticket=SLldR448CUU%3d&portalid=1"
    )
    assert parsed_items[1]["description"] == (
        "Meeting Agenda: "
        "http://bos.lacounty.gov/LinkClick.aspx?fileticket=hud9uxGbJns%3d&portalid=1"
    )
    assert parsed_items[2]["description"] == (
        "Meeting Agenda: "
        "http://bos.lacounty.gov/LinkClick.aspx?fileticket=pztBtVCl0QI%3d&portalid=1\n"
        "Supplemental Agenda: "
        "http://bos.lacounty.gov/LinkClick.aspx?fileticket=WyvnLwMAY24%3d&portalid=1"
    )
    assert parsed_items[3]["description"] == (
        "Meeting Agenda: "
        "http://bos.lacounty.gov/LinkClick.aspx?fileticket=-gvODfqLCb0%3d&portalid=1"
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2021, 3, 23, 9, 30)
    assert parsed_items[1]["start"] == datetime(2021, 3, 16, 9, 30)
    assert parsed_items[2]["start"] == datetime(2021, 3, 9, 9, 30)
    assert parsed_items[3]["start"] == datetime(2021, 3, 2, 9, 30)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] is None
    assert parsed_items[2]["end"] is None
    assert parsed_items[3]["end"] is None


@pytest.mark.parametrize("item", parsed_items)
def test_time_notes(item):
    assert item["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "la_county_bos/202103230930/x/regular_meeting"
    assert parsed_items[1]["id"] == "la_county_bos/202103160930/x/special_meeting"
    assert parsed_items[2]["id"] == "la_county_bos/202103090930/x/regular_meeting"
    assert (
        parsed_items[3]["id"]
        == "la_county_bos/202103020930/x/special_closed_session_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[1]["status"] == "passed"
    assert parsed_items[2]["status"] == "passed"
    assert parsed_items[3]["status"] == "passed"


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
                "http://bos.lacounty.gov/LinkClick.aspx"
                "?fileticket=uubFVO4njSk%3d&portalid=1"
            ),
            "title": "Meeting/Agenda Information",
        },
        {
            "href": (
                "http://bos.lacounty.gov/LinkClick.aspx"
                "?fileticket=SLldR448CUU%3d&portalid=1"
            ),
            "title": "Supplemental Agenda",
        },
    ]
    assert parsed_items[1]["links"] == [
        {
            "href": (
                "http://bos.lacounty.gov/LinkClick.aspx"
                "?fileticket=hud9uxGbJns%3d&portalid=1"
            ),
            "title": "Meeting/Agenda Information",
        },
    ]
    assert parsed_items[2]["links"] == [
        {
            "href": (
                "http://bos.lacounty.gov/LinkClick.aspx"
                "?fileticket=pztBtVCl0QI%3d&portalid=1"
            ),
            "title": "Meeting/Agenda Information",
        },
        {
            "href": (
                "http://bos.lacounty.gov/LinkClick.aspx"
                "?fileticket=WyvnLwMAY24%3d&portalid=1"
            ),
            "title": "Supplemental Agenda",
        },
    ]
    assert parsed_items[3]["links"] == [
        {
            "href": (
                "http://bos.lacounty.gov/LinkClick.aspx"
                "?fileticket=-gvODfqLCb0%3d&portalid=1"
            ),
            "title": "Meeting/Agenda Information",
        },
    ]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
