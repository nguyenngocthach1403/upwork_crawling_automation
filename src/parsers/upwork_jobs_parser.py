from bs4 import BeautifulSoup
from typing import List, Dict, Optional

from src.parsers.parser import parse_upwork_time


class JobListParser:
    """
    Parse job list from Upwork search HTML
    """

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def parse(self) -> List[Dict]:
        """
        Extract job_id + posted_at from HTML

        :return: List[dict]
        """

        job_card_tags = self.soup.find_all("article")
        jobs = []

        for tag in job_card_tags:
            job_id = tag.get("data-ev-job-uid")
            if not job_id:
                continue

            posted_at = self._parse_posted_time(tag)

            jobs.append({
                "job_id": job_id,
                "posted_at": posted_at
            })

        return jobs

    # =============================
    # Private Helpers
    # =============================

    def _parse_posted_time(self, tag) -> Optional[int]:
        try:
            time_tag = tag.find("small", {"data-test": "job-published-date"})
            if not time_tag:
                return None

            text = time_tag.get_text(strip=True)
            return parse_upwork_time(text)

        except Exception:
            return None
