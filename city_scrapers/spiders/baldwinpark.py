from city_scrapers.spiders.granicus import GranicusSpider


class BaldwinparkSpider(GranicusSpider):
    name = "baldwinpark"
    agency = "Baldwin Park"
    sub_agency = "City"
    start_urls = ["https://baldwinpark.granicus.com/ViewPublisher.php?view_id=10"]
    location = {
        "name": "",
        "address": "14403 Pacific Ave, Baldwin Park, CA 91706",
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
