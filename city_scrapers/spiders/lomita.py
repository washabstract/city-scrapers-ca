from city_scrapers.spiders.granicus import GranicusSpider


class LomitaSpider(GranicusSpider):
    name = "lomita"
    agency = "Lomita"
    sub_agency = "City"
    start_urls = ["https://lomita.granicus.com/ViewPublisher.php?view_id=3"]
    location = {
        "name": "",
        "address": "24300 NARBONNE AVENUE, LOMITA, CA 90717",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(
            self.name,
            self.agency,
            self.location,
            self.sub_agency,
            None,
            *args,
            **kwargs,
        )
