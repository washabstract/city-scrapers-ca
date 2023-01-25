from city_scrapers.spiders.granicus import GranicusSpider


class DuarteSpider(GranicusSpider):
    name = "duarte"
    agency = "Duarte"
    sub_agency = "City"
    start_urls = ["https://accessduarte.granicus.com/ViewPublisher.php?view_id=12"]
    location = {
        "name": "",
        "address": "1600 Huntington Dr, Duarte, CA 91010",
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