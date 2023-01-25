from city_scrapers.spiders.granicus import GranicusSpider


class LapuenteSpider(GranicusSpider):
    name = "lapuente"
    agency = "La Puente"
    sub_agency = "Planning Commission"
    start_urls = [
        # Planning Commission
        "https://lapuente.granicus.com/ViewPublisher.php?view_id=3",
        # City Council
        "https://lapuente.granicus.com/ViewPublisher.php?view_id=2",
    ]
    location = {
        "name": "",
        "address": "CITY HALL COUNCIL CHAMBERS 15900 E. MAIN STREET, LA PUENTE",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(
            self.name,
            self.agency,
            self.sub_agency,
            self.location,
            self.table_classes,
            *args,
            **kwargs,
        )
