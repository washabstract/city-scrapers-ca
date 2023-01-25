from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.lomita import LomitaSpider

start_url = "https://lomita.granicus.com/ViewPublisher.php?view_id=3"

test_response = file_response(
    join(dirname(__file__), "files", "lomita.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "lomita_agenda_1.pdf"),
    mode="rb",
    url=start_url,
)
spider = LomitaSpider()

freezer = freeze_time("2022-12-06")
freezer.start()

agenda_start_time = spider._parse_pdf_start_time(agenda_response)
parsed_items = [item for item in spider.parse(test_response)]
parsed_items[1] = next(
    spider._parse_agenda(
        agenda_response,
        parsed_items[1].cb_kwargs["meeting"],
        parsed_items[1].cb_kwargs["item"],
    )
)
parsed_items = parsed_items[:2] + [
    item.cb_kwargs["meeting"] if type(item) != Meeting else item
    for item in parsed_items[2:]
]
freezer.stop()


def test_number_parsed():
    assert len(parsed_items) > 100


def test_title():
    assert parsed_items[0]["title"] == "Lomita City Council Meeting"
    assert parsed_items[2]["title"] == "Lomita City Council Special Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 20, 18, 0)
    assert agenda_start_time == datetime(2022, 12, 6, 18, 0)
    assert parsed_items[1]["start"] == datetime(2022, 12, 7, 18, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] == datetime(2022, 12, 7, 18, 0)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "lomita/202212201800/x/lomita_city_council_meeting"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "24300 NARBONNE AVENUE, LOMITA, CA 90717",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == []

    assert parsed_items[1]["links"] == [
        {
            "title": "Agenda & Reports",
            "href": "https://lomita.granicus.com/"
            "AgendaViewer.php?view_id=3&clip_id=780",
        },
        {
            "title": "Video",
            "href": "https://lomita.granicus.com/"
            "MediaPlayer.php?view_id=3&clip_id=780",
        },
        {
            "title": "Open Video Only in Windows Media Player",
            "href": "https://lomita.granicus.com"
            "/ASX.php?view_id=3&clip_id=780&sn=lomita.granicus.com",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[2]["classification"] == CITY_COUNCIL


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
