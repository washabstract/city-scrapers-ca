from city_scrapers.spiders.granicus import GranicusSpider


class RosemeadSpider(GranicusSpider):
    name = "rosemead"
    agency = "Rosemead"
    sub_agency = "City"
    start_urls = ["https://cityofrosemead.granicus.com/ViewPublisher.php?view_id=2"]
    location = {
        "name": "City Hall Council Chambers",
        "address": "8838 E. Valley Blvd. Rosemead, CA 91770",
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
