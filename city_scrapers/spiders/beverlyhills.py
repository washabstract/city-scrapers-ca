from city_scrapers.spiders.granicus import GranicusSpider


class BeverlyhillsSpider(GranicusSpider):
    name = "beverlyhills"
    agency = "Beverly Hills"
    sub_agency = "City"
    start_urls = ["https://beverlyhills.granicus.com/ViewPublisher.php?view_id=57"]
    location = {
        "name": "",
        "address": "Room 280A, 455 North Rexford Drive,"
        " Beverly Hills, California 90210",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(
            self.name,
            self.agency,
            self.sub_agency,
            self.location,
            None,
            *args,
            **kwargs,
        )
