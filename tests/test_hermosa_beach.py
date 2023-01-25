from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.hermosa_beach import HermosaBeachSpider

start_url = "https://hermosabeach.granicus.com/ViewPublisher.php?view_id=6"
test_response = file_response(
    join(dirname(__file__), "files", "hermosa_beach.html"),
    url=start_url,
)
agenda_response = file_response(
    join(dirname(__file__), "files", "hermosa_beach_agenda_1.pdf"),
    url=start_url,
    mode="rb",
)

spider = HermosaBeachSpider()

freezer = freeze_time("2023-01-3")
freezer.start()

agenda_start_time = spider._parse_pdf_start_time(agenda_response)
parsed_items = [
    item.cb_kwargs["meeting"] if type(item) != Meeting else item
    for item in spider.parse(test_response)
]

freezer.stop()


def test_number_parsed():
    assert len(parsed_items) > 300


def test_title():
    assert (
        parsed_items[0]["title"] == "City Council Hybrid Meeting "
        "(Closed Session - 5:00 PM and Open Session - 6:00 PM)"
    )


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2023, 1, 10, 17, 0)
    assert agenda_start_time == datetime(2023, 1, 3, 17, 00)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "hermosa_beach/202301101700/x"
        "/city_council_hybrid_meeting_closed_session_5_00_pm_and_open_session_6_00_pm_"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Hall",
        "address": "1315 Valley Drive Hermosa Beach, CA 90254",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert len(parsed_items[0]["links"]) == 1
    assert parsed_items[0]["links"] == [
        {
            "href": "https://hermosabeach.granicus.com"
            "/AgendaViewer.php?view_id=6&event_id=3832",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
