from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import (
    BOARD,
    CANCELLED,
    CITY_COUNCIL,
    COMMISSION,
    NOT_CLASSIFIED,
    TENTATIVE,
)
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.items import Meeting
from city_scrapers.spiders.granicus import GranicusSpider

# Tested on Baldwin Park, Beverly Hills, Burbanl, City of Duarte, City of Gardena
baldwin_park_start_url = "https://baldwinpark.granicus.com/ViewPublisher.php?view_id=10"
beverlyhills_start_url = (
    "https://beverlyhills.granicus.com/ViewPublisher.php?view_id=57"
)
burbank_start_url = "https://burbank.granicus.com/ViewPublisher.php?view_id=6"
duarte_start_url = "https://accessduarte.granicus.com/ViewPublisher.php?view_id=12"
gardena_start_url = "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=6"

# Baldwinpark
baldwin_test_response = file_response(
    join(dirname(__file__), "files", "baldwinpark.html"),
    url=baldwin_park_start_url,
)

# Beverlyhills
test_beverly_hills_response = file_response(
    join(dirname(__file__), "files", "beverlyhills.html"),
    url=beverlyhills_start_url,
)

# burbank
test_burbank_response = file_response(
    join(dirname(__file__), "files", "burbank.html"),
    url=burbank_start_url,
)

# accessduarte
test_duarte_response = file_response(
    join(dirname(__file__), "files", "duarte.html"),
    url=duarte_start_url,
)

# cityofgardena
test_city_of_gardena_response = file_response(
    join(dirname(__file__), "files", "cityofgardena.html"),
    url=gardena_start_url,
)


baldwin_park_spider = GranicusSpider(
    name="baldwinpark",
    agency="Baldwin Park",
    sub_agency="Planning Commission",
    start_urls=[baldwin_park_start_url],
)
beverly_hills_spider = GranicusSpider(
    name="beverlyhills",
    agency="Beverly Hills",
    sub_agency="Planning Commission",
    start_urls=[beverlyhills_start_url],
)
burbank_spider = GranicusSpider(
    name="burbank",
    agency="Burbank",
    sub_agency="Planning Commission",
    start_urls=[burbank_start_url],
)
duarte_spider = GranicusSpider(
    name="duartecity",
    agency="Duarte",
    sub_agency="Planning Commission",
    start_urls=[duarte_start_url],
)
gardena_spider = GranicusSpider(
    name="gardenacity",
    agency="Gardena",
    sub_agency="Planning Commission",
    start_urls=[gardena_start_url],
)


freezer = freeze_time("2022-11-08")
freezer.start()

baldwin_parsed_items = [
    item for item in baldwin_park_spider.parse(baldwin_test_response)
]
beverlyhills_parsed_items = [
    item for item in beverly_hills_spider.parse(test_beverly_hills_response)
]
burbank_parsed_items = [item for item in burbank_spider.parse(test_burbank_response)]
accessduarte_parsed_items = [item for item in duarte_spider.parse(test_duarte_response)]
citygardena_parsed_items = [
    item for item in gardena_spider.parse(test_city_of_gardena_response)
]

baldwin_agenda_1 = file_response(
    join("tests", "files", "baldwinpark_agenda_1.pdf"),
    mode="rb",
    url=baldwin_park_start_url,
)

beverlyhills_agenda_1 = file_response(
    join("tests", "files", "beverlyhills_agenda_1.pdf"),
    mode="rb",
    url=beverlyhills_start_url,
)

burbank_agenda_1 = file_response(
    join("tests", "files", "burbank_agenda_1.pdf"), mode="rb", url=burbank_start_url
)

duarte_agenda_1 = file_response(
    join("tests", "files", "duarte_agenda_1.pdf"), mode="rb", url=duarte_start_url
)

gardena_agenda_1 = file_response(
    join("tests", "files", "gardena_agenda_1.pdf"), mode="rb", url=gardena_start_url
)

# Converting all the items from Request objects to Meeting objects
# Except the specific items we use to test the pdf agendas
baldwin_agenda_index = 8
baldwin_parsed_items = list(
    map(
        lambda item: item[1].cb_kwargs["meeting"]
        if type(item[1]) != Meeting and item[0] != baldwin_agenda_index
        else item[1],
        enumerate(baldwin_parsed_items),
    )
)
beverlyhills_parsed_items = [beverlyhills_parsed_items[0]] + list(
    map(
        lambda item: item.cb_kwargs["meeting"] if type(item) != Meeting else item,
        beverlyhills_parsed_items[1:],
    )
)
burbank_parsed_items = [burbank_parsed_items[0]] + list(
    map(
        lambda item: item.cb_kwargs["meeting"] if type(item) != Meeting else item,
        burbank_parsed_items[1:],
    )
)
accessduarte_parsed_items = [accessduarte_parsed_items[0]] + list(
    map(
        lambda item: item.cb_kwargs["meeting"] if type(item) != Meeting else item,
        accessduarte_parsed_items[1:],
    )
)
citygardena_parsed_items = [citygardena_parsed_items[0]] + list(
    map(
        lambda item: item.cb_kwargs["meeting"] if type(item) != Meeting else item,
        citygardena_parsed_items[1:],
    )
)


# parsing the items with the agenda
baldwin_parsed_items[baldwin_agenda_index] = next(
    baldwin_park_spider._parse_agenda(
        baldwin_agenda_1,
        baldwin_parsed_items[baldwin_agenda_index].cb_kwargs["meeting"],
        baldwin_parsed_items[baldwin_agenda_index].cb_kwargs["item"],
    )
)

beverlyhills_parsed_items[0] = next(
    beverly_hills_spider._parse_agenda(
        beverlyhills_agenda_1,
        beverlyhills_parsed_items[0].cb_kwargs["meeting"],
        beverlyhills_parsed_items[0].cb_kwargs["item"],
    )
)

burbank_parsed_items[0] = next(
    burbank_spider._parse_agenda(
        burbank_agenda_1,
        burbank_parsed_items[0].cb_kwargs["meeting"],
        burbank_parsed_items[0].cb_kwargs["item"],
    )
)

accessduarte_parsed_items[0] = next(
    duarte_spider._parse_agenda(
        duarte_agenda_1,
        accessduarte_parsed_items[0].cb_kwargs["meeting"],
        accessduarte_parsed_items[0].cb_kwargs["item"],
    )
)

citygardena_parsed_items[0] = next(
    gardena_spider._parse_agenda(
        gardena_agenda_1,
        citygardena_parsed_items[0].cb_kwargs["meeting"],
        citygardena_parsed_items[0].cb_kwargs["item"],
    )
)


freezer.stop()


def filter_first(function, iterable):
    """
    Returns the first item that is True
    """
    for i in iterable:
        if function(i):
            return i

    return None


def test_title():
    assert (
        baldwin_parsed_items[0]["title"] == "Baldwin Park City Council Special Meeting"
    )
    assert baldwin_parsed_items[1]["title"] == "Baldwin Park Finance Authority Meeting"
    assert (
        beverlyhills_parsed_items[0]["title"] == "Planning Commission Regular Meeting"
    )
    assert burbank_parsed_items[0]["title"] == "Parks and Recreation Board"
    assert (
        accessduarte_parsed_items[0]["title"]
        == "Planning Commission Meeting- Cancelled"
    )
    assert citygardena_parsed_items[0]["title"] == "Cancellation Notice"


def test_description():
    assert baldwin_parsed_items[0]["description"] == ""


def test_start():
    # TODO Testing meeting that need to get date and time through agenda
    assert baldwin_parsed_items[0]["start"] == datetime(2022, 11, 16, 17, 0)
    assert beverlyhills_parsed_items[0]["start"] == datetime(2022, 11, 10, 13, 30)
    assert burbank_parsed_items[0]["start"] == datetime(2022, 11, 10, 18, 0)
    assert accessduarte_parsed_items[0]["start"] == datetime(2022, 11, 21, 19, 0)
    assert citygardena_parsed_items[0]["start"] == datetime(2022, 11, 15, 19, 0)


def test_end():
    assert baldwin_parsed_items[0]["end"] is None
    assert beverlyhills_parsed_items[0]["end"] is None
    assert burbank_parsed_items[0]["end"] is None
    assert accessduarte_parsed_items[0]["end"] is None
    assert citygardena_parsed_items[0]["end"] is None

    # Find the items with duration
    baldwin_end = filter_first(
        lambda item: item["end"] is not None, baldwin_parsed_items
    )
    beverlyhills_end = filter_first(
        lambda item: item["end"] is not None, beverlyhills_parsed_items
    )
    burbank_end = filter_first(
        lambda item: item["end"] is not None, burbank_parsed_items
    )
    duarte_end = filter_first(
        lambda item: item["end"] is not None, accessduarte_parsed_items
    )
    gardena_end = filter_first(
        lambda item: item["end"] is not None, citygardena_parsed_items
    )

    assert baldwin_end["end"] == datetime(2022, 11, 2, 0, 13)
    assert beverlyhills_end["end"] == datetime(2022, 10, 27, 3, 17)
    assert burbank_end is None
    assert duarte_end["end"] == datetime(2022, 11, 8, 0, 44)
    assert gardena_end is None


def test_time_notes():
    assert baldwin_parsed_items[0]["time_notes"] == ""
    assert beverlyhills_parsed_items[0]["time_notes"] == ""
    assert burbank_parsed_items[0]["time_notes"] == ""
    assert accessduarte_parsed_items[0]["time_notes"] == ""
    assert citygardena_parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        baldwin_parsed_items[0]["id"]
        == "baldwinpark/202211161700/x/baldwin_park_city_council_special_meeting"
    )
    assert (
        beverlyhills_parsed_items[0]["id"]
        == "beverlyhills/202211101330/x/planning_commission_regular_meeting"
    )
    assert (
        burbank_parsed_items[0]["id"]
        == "burbank/202211101800/x/parks_and_recreation_board"
    )
    assert (
        accessduarte_parsed_items[0]["id"]
        == "duartecity/202211211900/x/planning_commission_meeting"
    )
    assert citygardena_parsed_items[0]["id"] == "gardenacity/202211151900/x/notice"


def test_status():
    assert baldwin_parsed_items[0]["status"] == TENTATIVE
    assert beverlyhills_parsed_items[0]["status"] == TENTATIVE
    assert burbank_parsed_items[0]["status"] == TENTATIVE
    assert accessduarte_parsed_items[0]["status"] == CANCELLED
    assert citygardena_parsed_items[0]["status"] == CANCELLED


def test_location():
    assert baldwin_parsed_items[0]["location"] == {"name": "", "address": ""}


def test_source():
    assert (
        baldwin_parsed_items[0]["source"]
        == "https://baldwinpark.granicus.com/ViewPublisher.php?view_id=10"
    )
    assert (
        beverlyhills_parsed_items[0]["source"]
        == "https://beverlyhills.granicus.com/ViewPublisher.php?view_id=57"
    )
    assert (
        burbank_parsed_items[0]["source"]
        == "https://burbank.granicus.com/ViewPublisher.php?view_id=6"
    )
    assert (
        accessduarte_parsed_items[0]["source"]
        == "https://accessduarte.granicus.com/ViewPublisher.php?view_id=12"
    )
    assert (
        citygardena_parsed_items[0]["source"]
        == "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=6"
    )


def test_links():
    assert baldwin_parsed_items[0]["links"] == []
    # Find the first item that includes a link.
    baldwin_links = filter_first(
        lambda item: len(item["links"]) > 0, baldwin_parsed_items
    )
    assert baldwin_links is not None
    assert baldwin_links["links"] == (
        [
            {
                "title": "Agenda",
                "href": "https://baldwinpark.granicus.com"
                "/AgendaViewer.php?view_id=10&clip_id=3300",
            },
            {
                "title": "Listen to Audio",
                "href": "https://baldwinpark.granicus.com"
                "/MediaPlayer.php?view_id=10&clip_id=3300",
            },
        ]
    )

    beverly_links = filter_first(
        lambda item: len(item["links"]) > 1, beverlyhills_parsed_items
    )
    burbank_links = filter_first(
        lambda item: len(item["links"]) > 0, burbank_parsed_items
    )
    duarte_links = filter_first(
        lambda item: len(item["links"]) > 1, accessduarte_parsed_items
    )
    gardena_links = filter_first(
        lambda item: len(item["links"]) > 2, citygardena_parsed_items
    )

    assert beverly_links["links"] == (
        [
            {
                "title": "Video",
                "href": "https://beverlyhills.granicus.com"
                "/MediaPlayer.php?view_id=57&clip_id=8862",
            },
            {
                "title": "Open Video Only in Windows Media Player",
                "href": "https://beverlyhills.granicus.com"
                "/ASX.php?view_id=57&clip_id=8862&sn=beverlyhills.granicus.com",
            },
            {
                "title": "Audio",
                "href": "https://archive-video.granicus.com"
                "/beverlyhills/beverlyhills_647226ec-56e4-11ed-95a3-0050569183fa.mp3",
            },
            {
                "title": "Agenda",
                "href": "https://beverlyhills.granicus.com"
                "/AgendaViewer.php?view_id=57&clip_id=8862",
            },
            {
                "title": "Captions",
                "href": "https://beverlyhills.granicus.com"
                "/TranscriptViewer.php?view_id=57&clip_id=8862",
            },
        ]
    )

    assert burbank_links["links"] == (
        [
            {
                "title": "Agenda",
                "href": "https://burbank.granicus.com"
                "/AgendaViewer.php?view_id=6&event_id=7942",
            }
        ]
    )

    assert duarte_links["links"] == (
        [
            {
                "title": "Agenda",
                "href": "https://accessduarte.granicus.com"
                "/AgendaViewer.php?view_id=12&clip_id=986",
            },
            {
                "title": "Packet",
                "href": "https://d3n9y02raazwpg.cloudfront.net"
                "/accessduarte/99b95cf6-b41e-439a-ae41-4d8042de8f66"
                "-7801a13e-aeac-47ca-a441-9aaabd1209f9-1667516546.pdf",
            },
            {
                "title": "Video",
                "href": "https://accessduarte.granicus.com"
                "/MediaPlayer.php?view_id=12&clip_id=986",
            },
        ]
    )

    assert gardena_links["links"] == (
        [
            {
                "title": "Agenda",
                "href": "https://cityofgardena.granicus.com"
                "/AgendaViewer.php?view_id=6&event_id=386",
            },
            {
                "title": "Minutes",
                "href": "https://cityofgardena.granicus.com"
                "/services/minutes/reports/16250409-6a3b-"
                "4225-b359-994dfb5ee90a/attachment",
            },
            {
                "title": "Agenda Packet",
                "href": "https://d3n9y02raazwpg.cloudfront.net"
                "/cityofgardena/f03d6fce-68db-11ec-85e3-0050569183fa"
                "-97b9b753-b9c2-4753-9d7c-1f5e0b332a7e-1655849722.pdf",
            },
        ]
    )


def test_classification():
    assert baldwin_parsed_items[0]["classification"] == CITY_COUNCIL
    assert beverlyhills_parsed_items[0]["classification"] == COMMISSION
    assert burbank_parsed_items[0]["classification"] == BOARD
    assert accessduarte_parsed_items[0]["classification"] == COMMISSION
    assert citygardena_parsed_items[0]["classification"] == NOT_CLASSIFIED


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
