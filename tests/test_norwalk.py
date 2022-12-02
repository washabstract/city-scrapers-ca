from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.granicus import GranicusSpider

start_url = "https://norwalk.granicus.com/ViewPublisher.php?view_id=1"

test_response = file_response(
    join(dirname(__file__), "files", "norwalk.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "norwalk_agenda_1.pdf"),
    mode="rb",
    url=start_url,
)

spider = GranicusSpider(
    name="norwalk",
    agency="Norwalk",
    sub_agency="Something",
    location={"name": "Norwalk", "address": "123 Test Ave"},
    start_urls=[start_url],
)

freezer = freeze_time("2022-11-29")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
agenda_start_time = spider._parse_pdf_start_time(agenda_response)
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
    assert (
        parsed_items[0]["title"]
        == "Successor Agency for the Norwalk Redevelopment Agency Meeting"
    )


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 6, 18, 0)
    assert agenda_start_time == datetime(2022, 11, 29, 17, 45)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[4]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "norwalk/202212061800/x/"
        "successor_agency_for_the_norwalk_redevelopment_agency_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {"name": "Norwalk", "address": "123 Test Ave"}


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[4]["links"] == [
        {
            "title": "Agenda",
            "href": "https://norwalk.granicus.com"
            "/AgendaViewer.php?view_id=1&clip_id=751",
        },
        {
            "title": "Synopsis",
            "href": "https://norwalk.granicus.com"
            "/MinutesViewer.php?view_id=1&clip_id=751"
            "&doc_id=647e474d-67a6-11ed-95a3-0050569183fa",
        },
        {
            "title": "Video/Audio",
            "href": "https://norwalk.granicus.com"
            "/MediaPlayer.php?view_id=1&clip_id=751",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
