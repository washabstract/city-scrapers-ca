from city_scrapers.spiders.granicus import GranicusSpider


class PalosVerdesEstatesSpider(GranicusSpider):
    name = "palos_verdes_estates"
    agency = "Palos Verdes Estates"
    sub_agency = "City"
    start_urls = ["https://pvestates.granicus.com/ViewPublisher.php?view_id=1"]
    location = {
        "name": "Council Chambers of City Hall",
        "address": "340 Palos Verdes Drive West Palos Verdes Estates, CA 90274",
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
