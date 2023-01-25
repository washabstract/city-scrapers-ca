from city_scrapers.spiders.granicus import GranicusSpider


class PalmdaleSpider(GranicusSpider):
    name = "palmdale"
    agency = "Palmdale"
    sub_agency = "City"
    start_urls = ["https://palmdale.granicus.com/ViewPublisher.php?view_id=22"]
    location = {
        "name": "City Council Chamber",
        "address": "38300 Sierra Hwy, Palmdale, CA 93550",
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
