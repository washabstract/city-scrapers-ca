from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.la_canada_flintridge import LaCanadaFlintridgeSpider

start_url = "https://lacanadaflintridge-ca.granicus.com/ViewPublisher.php?view_id=4"
test_response = file_response(
    join(dirname(__file__), "files", "la_canada_flintridge.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "la_canada_flintridge_agenda_1.pdf"),
    url=start_url,
    mode="rb",
)

spider = LaCanadaFlintridgeSpider()

freezer = freeze_time("2022-12-08")
freezer.start()

agenda_start_time = spider._parse_pdf_start_time(agenda_response)
parsed_items = [
    item.cb_kwargs["meeting"] if type(item) != Meeting else item
    for item in spider.parse(test_response)
]


freezer.stop()


def test_number_parsed():
    assert len(parsed_items) > 100


def test_title():
    assert parsed_items[0]["title"] == "Planning Commission Notice of Adjourned Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 8, 18, 30)
    assert agenda_start_time == datetime(2022, 12, 8, 18, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[3]["end"] == datetime(2022, 12, 6, 16, 39)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "la_canada_flintridge/202212081830/x/"
        "planning_commission_notice_of_adjourned_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Hall Council Chambers",
        "address": "One Civic Center Drive, La Cañada Flintridge, CA 91011",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://lacanadaflintridge-ca.granicus.com"
            "/AgendaViewer.php?view_id=4&event_id=1108",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
