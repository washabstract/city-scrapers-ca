from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.lapuente import LapuenteSpider

start_url = "https://lapuente.granicus.com/ViewPublisher.php?view_id=3"

agenda_response = file_response(
    join(dirname(__file__), "files", "lapuente_agenda_1.pdf"),
    mode="rb",
    url=start_url,
)

agenda_response_2 = file_response(
    join(dirname(__file__), "files", "lapuente_agenda_2.pdf"),
    mode="rb",
    url=start_url,
)

test_response = file_response(
    join(dirname(__file__), "files", "lapuente.html"),
    url=start_url,
)
spider = LapuenteSpider()

freezer = freeze_time("2022-12-05")
freezer.start()

agenda_start_time = spider._parse_pdf_start_time(agenda_response)
parsed_items = [item for item in spider.parse(test_response)]

parsed_items[0] = next(
    spider._parse_agenda(
        agenda_response,
        parsed_items[0].cb_kwargs["meeting"],
        parsed_items[0].cb_kwargs["item"],
    )
)

parsed_items[1] = next(
    spider._parse_agenda(
        agenda_response_2,
        parsed_items[1].cb_kwargs["meeting"],
        parsed_items[1].cb_kwargs["item"],
    )
)

parsed_items = parsed_items[:2] + [
    item.cb_kwargs["meeting"] if type(item) != Meeting else item
    for item in parsed_items[2:]
]

freezer.stop()


def test_timezone():
    assert spider.timezone == "America/Los_Angeles"


def test_number_parsed():
    assert len(parsed_items) > 100


def test_title():
    assert parsed_items[0]["title"] == "Planning Commission"
    assert parsed_items[1]["title"] == "Special Planning Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 6, 19, 0)
    assert agenda_start_time == datetime(2022, 12, 5, 19, 0)
    assert parsed_items[1]["start"] == datetime(2022, 10, 18, 19, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] == datetime(2022, 10, 18, 19, 18)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "lapuente/202212061900/x/planning_commission"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "CITY HALL COUNCIL CHAMBERS 15900 E. MAIN STREET, LA PUENTE",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "View Agenda",
            "href": "https://lapuente.granicus.com/"
            "AgendaViewer.php?view_id=3&event_id=1088",
        }
    ]

    assert parsed_items[1]["links"] == [
        {
            "title": "View Agenda",
            "href": "https://lapuente.granicus.com"
            "/AgendaViewer.php?view_id=3&clip_id=2144",
        },
        {
            "title": "Listen to Audio",
            "href": "https://lapuente.granicus.com"
            "/MediaPlayer.php?view_id=3&clip_id=2144",
        },
        {
            "title": "Open Audio Only in Windows Media Player",
            "href": "https://lapuente.granicus.com"
            "/ASX.php?view_id=3&clip_id=2144&sn=lapuente.granicus.com",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
