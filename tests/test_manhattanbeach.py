from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.manhattanbeach import ManhattanbeachSpider

start_url = "https://manhattanbeach.granicus.com/ViewPublisher.php?view_id=7"
agenda_response = file_response(
    join(dirname(__file__), "files", "manhattanbeach_agenda_1.pdf"),
    mode="rb",
    url=start_url,
)

test_response = file_response(
    join(dirname(__file__), "files", "manhattanbeach.html"),
    url=start_url,
)
spider = ManhattanbeachSpider()

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


def test_timezone():
    assert spider.timezone == "America/Los_Angeles"


def test_number_parsed():
    assert len(parsed_items) > 100


def test_title():
    assert parsed_items[0]["title"] == "Planning Commission - Regular Meeting"
    assert parsed_items[1]["title"] == "Planning Commission - Regular Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 14, 15, 0)
    # assert agenda_start_time == datetime(2022, 12, 5, 19, 0)
    assert parsed_items[1]["start"] == datetime(2022, 11, 9, 15, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[1]["end"] == datetime(2022, 11, 9, 16, 2)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "manhattanbeach/202212141500/x/planning_commission_regular_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE
    assert parsed_items[1]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "City Council Chambers "
        "1400 Highland Avenue, Manhattan Beach, CA 90266",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == []

    assert parsed_items[1]["links"] == [
        {
            "title": "Nov 09, 22",
            "href": "https://manhattanbeach.granicus.com"
            "/MediaPlayer.php?view_id=7&clip_id=4021",
        },
        {
            "title": "Agenda",
            "href": "https://manhattanbeach.granicus.com"
            "/AgendaViewer.php?view_id=7&clip_id=4021",
        },
        {
            "title": "Video",
            "href": "https://archive-video.granicus.com"
            "/manhattanbeach/manhattanbeach_bb80209a-611c-11ed-95a3-0050569183fa.mp4",
        },
        {
            "title": "Captions",
            "href": "https://manhattanbeach.granicus.com"
            "/TranscriptViewer.php?view_id=7&clip_id=4021",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
