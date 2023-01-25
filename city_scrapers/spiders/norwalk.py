from city_scrapers.spiders.granicus import GranicusSpider


class NorwalkSpider(GranicusSpider):
    name = "norwalk"
    agency = "Norwalk"
    sub_agency = "City"
    start_urls = ["https://norwalk.granicus.com/ViewPublisher.php?view_id=1"]
    location = {
        "name": "Norwalk City Hall",
        "address": "12700 Norwalk Blvd, Norwalk, CA 90650",
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
