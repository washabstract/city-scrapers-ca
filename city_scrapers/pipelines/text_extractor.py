import re
from io import BytesIO

import pdfplumber
import requests


class TextExtractorPipeline:
    """Implements :class:`Pipeline` for PDF Text Extraction from meeting notes and agendas.
    Extracts and stores zoom meeting link if available
    """

    def process_item(self, item, spider):
        for link in item["links"]:
            """parse only the meeting/agenda link"""
            if link["title"] == "Meeting/Agenda Information":
                raw_extracted_text = ""
                """get pdf, open and extract pages"""
                with pdfplumber.open(
                    BytesIO(requests.get(link["href"]).content)
                ) as pdf:
                    for page in pdf.pages:
                        raw_extracted_text += page.extract_text()
                        """search for zoom link in first page, store as meeting URL"""
                        if page == pdf.pages[0]:
                            meeting_link = re.search(
                                r"https://(.+?\.)?zoom.us/j/.+?\b",
                                raw_extracted_text,
                                re.M,
                            ).group()
                            item["location"]["url"] = (
                                meeting_link if meeting_link else ""
                            )
                    link["raw_text"] = raw_extracted_text
        return item
