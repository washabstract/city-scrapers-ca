import re
from io import BytesIO

import pdfplumber
import requests
from pdfminer.pdfparser import PDFSyntaxError


class TextExtractorPipeline:
    """Implements :class:`Pipeline` for PDF Text Extraction.
    Extracts and stores zoom meeting link if available
    """

    def extract_text(self, link):
        raw_extracted_text = ""
        meeting_link = None
        """get pdf, open and extract pages"""
        try:
            with pdfplumber.open(BytesIO(requests.get(link["url"]).content)) as pdf:
                for page in pdf.pages:
                    extracted_text = page.extract_text()
                    raw_extracted_text += extracted_text if extracted_text else ""
                    """search for zoom link in first page, store as meeting URL"""
                    if page == pdf.pages[0]:
                        meeting_link = re.search(
                            r"https://(.+?\.)?zoom.us/j/.+?\b",
                            raw_extracted_text,
                            re.M,
                        )
                        if meeting_link:
                            meeting_link = meeting_link.group().replace(
                                "\x00", "\uFFFD"
                            )
        except PDFSyntaxError:
            pass
        return raw_extracted_text.replace("\x00", "\uFFFD"), meeting_link

    def process_item(self, item, spider):
        for link in item["links"]:
            """parse only the meeting/agenda link"""
            if link["note"] == "Meeting/Agenda Information" or (
                "Agenda" in link["note"] and "HTML" not in link["note"]
            ):
                link["raw_text"], item["location"]["url"] = self.extract_text(link)
        return item
