from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, COMMITTEE, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.palmdale import PalmdaleSpider

palmdale_start_url = "https://palmdale.granicus.com/ViewPublisher.php?view_id=22"

test_response = file_response(
    join(dirname(__file__), "files", "palmdale.html"),
    url=palmdale_start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "palmdale_agenda_1.pdf"),
    mode="rb",
    url=palmdale_start_url,
)


spider = PalmdaleSpider()

freezer = freeze_time("2022-11-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

agenda_start_time = spider._parse_pdf_start_time(agenda_response)
# Converting Request objects to Meetings
parsed_items = list(
    map(
        lambda item: item.cb_kwargs["meeting"] if type(item) != Meeting else item,
        parsed_items,
    )
)

freezer.stop()


def test_number_parsed():
    assert len(parsed_items) > 100


def test_title():
    assert parsed_items[0]["title"] == "Measure AV Oversight Committee"
    assert parsed_items[2]["title"] == "Advisory Redistricting Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 11, 30, 17, 0)
    # testing that the time can be scraped from the agenda
    # Should be none in this case since the pdf's
    # content consists of images and not actual text
    assert agenda_start_time is None
    assert parsed_items[2]["start"] == datetime(2022, 2, 9, 17, 35)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[2]["end"] == datetime(2022, 2, 9, 19, 23)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "palmdale/202211301700/x/measure_av_oversight_committee"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[2]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Council Chamber",
        "address": "38300 Sierra Hwy, Palmdale, CA 93550",
    }


def test_source():
    assert parsed_items[0]["source"] == palmdale_start_url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://palmdale.granicus.com"
            "/AgendaViewer.php?view_id=22&event_id=2007",
            "title": "Agenda",
        },
        {
            "href": "https://d3n9y02raazwpg.cloudfront.net"
            "/palmdale/94579a19-44d7-11ed-95a3-"
            "0050569183fa-5083303a-9672-47e0-a899-13959013cb4c-1669253716.pdf",
            "title": "Agenda Packet",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
    assert parsed_items[2]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
