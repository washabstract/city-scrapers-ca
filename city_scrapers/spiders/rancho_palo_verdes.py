from city_scrapers.spiders.granicus import GranicusSpider


class RanchoPaloVerdesSpider(GranicusSpider):
    name = "rancho_palo_verdes"
    agency = "Rancho Palo Verdes"
    sub_agency = "City"
    start_urls = ["https://rpv.granicus.com/ViewPublisher.php?view_id=5"]
    location = {
        "name": "",
        "address": "29301 Hawthorne Blvd, Rancho Palos Verdes, CA 90275",
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
