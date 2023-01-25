from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.west_lake_village import WestLakeVillageSpider

start_url = "https://westlakevillage.granicus.com/viewpublisher.php?view_id=8"
test_response = file_response(
    join(dirname(__file__), "files", "west_lake_village.html"),
    url=start_url,
)
agenda_response = file_response(
    join(dirname(__file__), "files", "west_lake_village_agenda_1.pdf"),
    url=start_url,
    mode="rb",
)
spider = WestLakeVillageSpider()

freezer = freeze_time("2022-12-20")
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
    assert parsed_items[0]["title"] == "City Council Meeting - 1/11/2023"
    assert parsed_items[1]["title"] == "City Council Study Session Meeting - 1/25/2023"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2023, 1, 11, 18, 25)
    assert agenda_start_time == datetime(2022, 12, 20, 18, 30)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[7]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"] == "west_lake_village/202301111825/x/"
        "city_council_meeting_1_11_2023"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "title": "City Council Chambers",
        "href": "31200 Oak Crest Dr, Westlake Village, CA 91361, USA",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[6]["links"] == [
        {
            "href": "https://westlakevillage.granicus.com"
            "/AgendaViewer.php?view_id=8&clip_id=1327",
            "title": "Agenda",
        },
        {
            "href": "https://westlakevillage.granicus.com"
            "/MediaPlayer.php?view_id=8&clip_id=1327",
            "title": "Video",
        },
        {
            "href": "https://archive-video.granicus.com"
            "/westlakevillage/westlakevillage_8876e2da-9a43-4447-82ca-fb9cac13bfc0.mp4",
            "title": "MP4 Video",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
