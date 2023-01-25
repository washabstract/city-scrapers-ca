from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import CITY_COUNCIL, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.rancho_palo_verdes import RanchoPaloVerdesSpider

start_url = "https://rpv.granicus.com/ViewPublisher.php?view_id=5"
test_response = file_response(
    join(dirname(__file__), "files", "rancho_palo_verdes.html"),
    url=start_url,
)

agenda_response = file_response(
    join(dirname(__file__), "files", "rpv_agenda_1.pdf"),
    mode="rb",
    url=start_url,
)

spider = RanchoPaloVerdesSpider()

freezer = freeze_time("2022-12-01")
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
    assert parsed_items[0]["title"] == "City Council Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 12, 6, 19, 0)
    assert agenda_start_time == datetime(2022, 12, 1, 19, 0)


def test_end():
    assert parsed_items[0]["end"] is None
    assert parsed_items[7]["end"] == datetime(2022, 11, 15, 2, 39)


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "rancho_palo_verdes/202212061900/x/city_council_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "29301 Hawthorne Blvd, Rancho Palos Verdes, CA 90275",
    }


def test_source():
    assert parsed_items[0]["source"] == start_url


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://rpv.granicus.com/AgendaViewer.php?view_id=5&event_id=2083",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL
