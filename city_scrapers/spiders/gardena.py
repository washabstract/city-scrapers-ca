from city_scrapers.spiders.granicus import GranicusSpider


class GardenaSpider(GranicusSpider):
    name = "gardena"
    agency = "Gardena"
    sub_agency = "City"
    start_urls = [
        # Planning Commission
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=6",
        # City Council
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=1",
        # Finance committee
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=2",
        # Youth Commission
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=3",
        # Human services commission
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=5",
        # Discovered Planning Comission
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=6",
        # Recreation and parks comission
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=7",
        # Senior Citizen Commission
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=8",
        # Gardena Beautification Commission
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=9",
        # Gardena Economic Business Advisory Commission
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=10",
        # Gardena Rent Mediation Board
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=11",
        # Financing Agency
        "https://cityofgardena.granicus.com/ViewPublisher.php?view_id=12",
    ]
    location = {
        "name": "",
        "address": "1700 W 162nd St, Gardena, CA 90247",
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
