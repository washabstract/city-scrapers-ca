from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.palos_verdes_estates import PalosVerdesEstatesSpider

start_url = "https://pvestates.granicus.com/ViewPublisher.php?view_id=1"
test_response = file_response(
    join(dirname(__file__), "files", "palos_verdes_estates.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "palos_verdes_estates_agenda_1.pdf"),
    url=start_url,
    mode="rb",
)

spider = PalosVerdesEstatesSpider()

freezer = freeze_time("2022-12-8")
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
    assert parsed_items[0]["title"] == "Planning Commission Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 20, 18, 0)
    assert agenda_start_time == datetime(2022, 12, 8, 18, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[2]["end"] == datetime(2022, 12, 6, 4, 1)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "palos_verdes_estates/202212201800/x/"
        "planning_commission_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Council Chambers of City Hall",
        "address": "340 Palos Verdes Drive West Palos Verdes Estates, CA 90274",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://pvestates.granicus.com"
            "/AgendaViewer.php?view_id=1&event_id=1027",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
