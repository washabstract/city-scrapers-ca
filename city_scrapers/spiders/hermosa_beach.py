from city_scrapers.spiders.granicus import GranicusSpider


class HermosaBeachSpider(GranicusSpider):
    name = "hermosa_beach"
    agency = "Hermosa Beach"
    sub_agency = "City"
    start_urls = ["https://hermosabeach.granicus.com/ViewPublisher.php?view_id=6"]
    location = {
        "name": "City Hall",
        "address": "1315 Valley Drive Hermosa Beach, CA 90254",
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
