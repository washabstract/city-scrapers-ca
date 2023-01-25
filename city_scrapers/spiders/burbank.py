from city_scrapers.spiders.granicus import GranicusSpider


class BurbankSpider(GranicusSpider):
    name = "burbank"
    agency = "Burbank"
    sub_agency = "City"
    start_urls = ["https://burbank.granicus.com/ViewPublisher.php?view_id=6"]
    location = {
        "name": "",
        "address": "275 E Olive Ave, Burbank, CA 91502",
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
