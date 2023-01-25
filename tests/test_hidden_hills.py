from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.hidden_hills import HiddenHillsSpider

start_url = "https://hiddenhillscity.granicus.com/ViewPublisher.php?view_id=1"
test_response = file_response(
    join(dirname(__file__), "files", "hidden_hills.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "hidden_hills_agenda_1.pdf"),
    url=start_url,
    mode="rb",
)
spider = HiddenHillsSpider()

freezer = freeze_time("2023-01-1")
freezer.start()

agenda_start_time = spider._parse_pdf_start_time(agenda_response)
parsed_items = [
    item.cb_kwargs["meeting"] if type(item) != Meeting else item
    for item in spider.parse(test_response)
]
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "City Council Meeting 12-12-22"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 12, 17, 32)
    assert agenda_start_time == datetime(2023, 1, 1, 17, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 12, 12, 19, 17)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "hidden_hills/202212121732/x/city_council_meeting_12_12_22"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "6165 Spring Valley Rd, Hidden Hills, CA 91302",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://hiddenhillscity.granicus.com"
            "/AgendaViewer.php?view_id=1&clip_id=202",
            "title": "Agenda",
        },
        {
            "href": "https://hiddenhillscity.granicus.com"
            "/MediaPlayer.php?view_id=1&clip_id=202",
            "title": "Video",
        },
        {
            "href": "https://d3n9y02raazwpg.cloudfront.net"
            "/hiddenhillscity/b4ce93de-77ef-11ed-9024-0050569183fa-"
            "b3728b80-468e-4b70-8e50-ecf125ebc2d1-1670626008.pdf",
            "title": "Agenda Packet",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
