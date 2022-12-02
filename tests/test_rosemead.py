from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.granicus import GranicusSpider

start_url = "https://cityofrosemead.granicus.com/ViewPublisher.php?view_id=2"

test_response = file_response(
    join(dirname(__file__), "files", "rosemead.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "rosemead_agenda_1.pdf"),
    mode="rb",
    url=start_url,
)

spider = GranicusSpider(
    name="rosemead",
    agency="Rosemead",
    sub_agency="Something",
    location={"name": "Rosemead", "address": "123 Test Ave"},
    table_classes=["sortable"],
    start_urls=[start_url],
)

freezer = freeze_time("2022-12-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
agenda_start_time = spider._parse_pdf_start_time(agenda_response)

parsed_item_with_agenda = next(
    spider._parse_agenda(
        agenda_response,
        parsed_items[6].cb_kwargs["meeting"],
        parsed_items[6].cb_kwargs["item"],
    )
)

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
    assert parsed_items[0]["title"] == "Traffic Commission Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 1, 19, 0)
    assert parsed_item_with_agenda["start"] == datetime(2022, 11, 8, 19, 0)
    assert agenda_start_time == datetime(2022, 12, 1, 19, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_item_with_agenda["end"] == datetime(2022, 11, 8, 22, 43)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "rosemead/202212011900/x/traffic_commission_meeting"


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Rosemead",
        "address": "123 Test Ave",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_item_with_agenda["links"] == [
        {
            "title": "Agenda",
            "href": "https://cityofrosemead.granicus.com"
            "/AgendaViewer.php?view_id=2&clip_id=2741",
        },
        {
            "title": "Video",
            "href": "https://cityofrosemead.granicus.com"
            "/MediaPlayer.php?view_id=2&clip_id=2741",
        },
        {
            "title": "Open Video Only in Windows Media Player",
            "href": "https://cityofrosemead.granicus.com"
            "/ASX.php?view_id=2&clip_id=2741&sn=cityofrosemead.granicus.com",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
