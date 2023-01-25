from city_scrapers.spiders.granicus import GranicusSpider


class LaCanadaFlintridgeSpider(GranicusSpider):
    name = "la_canada_flintridge"
    agency = "LA Canada Flintridge"
    sub_agency = "City"
    start_urls = [
        "https://lacanadaflintridge-ca.granicus.com" "/ViewPublisher.php?view_id=4"
    ]
    location = {
        "name": "City Hall Council Chambers",
        "address": "One Civic Center Drive, La Cañada Flintridge, CA 91011",
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
