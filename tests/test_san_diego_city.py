from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import CITY_COUNCIL, PASSED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.san_diego_city import SanDiegoCitySpider

test_response = file_response(
    join(dirname(__file__), "files", "san_diego_city.html"),
    url="https://sandiego.granicus.com/ViewPublisher.php?view_id=3",
)

upcoming_response = file_response(
    join(dirname(__file__), "files", "san_diego_city_upcoming.html"),
    url="https://sandiego.hylandcloud.com/211agendaonlinecouncil",
)

spider = SanDiegoCitySpider()

freezer = freeze_time("2022-09-20")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_items_upcoming = [item for item in spider.parse(upcoming_response)]
# 11th object also contains meeting link
freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Special Agenda"
    assert parsed_items[11]["title"] == "Tuesday Agenda Revised Added S500-S508"
    assert parsed_items_upcoming[0]["title"] == "Adjourned Agenda"


def test_description():
    assert parsed_items[0]["description"] == ""
    assert parsed_items[11]["description"] == ""
    assert parsed_items_upcoming[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 19, 0, 0)
    assert parsed_items_upcoming[0]["start"] == datetime(2022, 9, 27, 10, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 9, 19, 7, 41)
    assert parsed_items_upcoming[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
    assert parsed_items[11]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "san_diego_city/202209190000/x/special_agenda"
    assert (
        parsed_items_upcoming[0]["id"]
        == "san_diego_city/202209271000/x/adjourned_agenda"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED
    assert parsed_items[11]["status"] == PASSED
    assert parsed_items_upcoming[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }

    assert parsed_items[11]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }

    assert parsed_items_upcoming[0]["location"] == {
        "name": "City Administration Building",
        "address": (
            "City Council Chambers - 12th Floor, 202 C Street San Diego, CA 92101"
        ),
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://sandiego.granicus.com/ViewPublisher.php?view_id=3"
    )
    assert (
        parsed_items[11]["source"]
        == "https://sandiego.granicus.com/ViewPublisher.php?view_id=3"
    )
    assert (
        parsed_items_upcoming[0]["source"]
        == "https://sandiego.hylandcloud.com/211agendaonlinecouncil"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=3&clip_id=8527",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/"
            "sandiego_f399b0df-ff5a-45b5-a6ac-b5c043699f0d.mp4",
        },
    ]

    assert parsed_items[11]["links"] == [
        {
            "title": "Video",
            "href": "https://sandiego.granicus.com"
            "/MediaPlayer.php?view_id=3&clip_id=8477",
        },
        {
            "title": "Minutes",
            "href": "https://sandiego.granicus.com"
            "/MinutesViewer.php?view_id=3&clip_id=8477",
        },
        {
            "title": "Video",
            "href": "http://archive-media.granicus.com:443"
            "/OnDemand/sandiego/"
            "sandiego_19ab90c2-2f55-41f5-98e9-dba3693f14de.mp4",
        },
    ]

    assert parsed_items_upcoming[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://sandiego.hylandcloud.com"
            "/211agendaonlinecouncil/Meetings/"
            "ViewMeeting?id=5262&doctype=1&site=council",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[11]["classification"] == CITY_COUNCIL
    assert parsed_items_upcoming[0]["classification"] == CITY_COUNCIL


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
