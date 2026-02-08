# src/parsers/upwork_job_detail.py

from bs4 import BeautifulSoup
import re
from typing import Optional


class UpworkJobDetailParser:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    # --------------------
    # Utils
    # --------------------
    @staticmethod
    def _clean(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _parse_relative_time(text: str) -> Optional[int]:
        """
        '11 hours ago' -> minutes
        """
        m = re.search(r"(\d+)\s+(minute|hour|day)s?\s+ago", text)
        if not m:
            return None

        value = int(m.group(1))
        unit = m.group(2)

        return {
            "minute": value,
            "hour": value * 60,
            "day": value * 1440
        }.get(unit)

    # --------------------
    # Core fields
    # --------------------
    def job_id(self) -> Optional[str]:
        el = self.soup.select_one("[data-ev-job-uid]")
        return el.get("data-ev-job-uid") if el else None

    def title(self) -> Optional[str]:
        el = self.soup.select_one("h4 span.flex-1")
        return self._clean(el.text) if el else None

    def posted_time_text(self) -> Optional[str]:
        el = self.soup.select_one('div[data-test="PostedOn"] span')
        return self._clean(el.text) if el else None

    def posted_minutes_ago(self) -> Optional[int]:
        text = self.posted_time_text()
        return self._parse_relative_time(text) if text else None

    def location(self) -> Optional[str]:
        el = self.soup.select_one('[data-test="LocationLabel"] p')
        return self._clean(el.text) if el else None

    def description(self) -> Optional[str]:
        el = self.soup.select_one('[data-test^="Description"] p')
        return self._clean(el.text) if el else None

    # --------------------
    # Budget / Type
    # --------------------
    def job_type(self) -> Optional[str]:
        el = self.soup.select_one('[data-cy="clock-timelog"]')
        return "hourly" if el else "fixed"


    def hourly_budget(self) -> Optional[dict]:
        li = self.soup.select_one('li:has([data-cy="clock-timelog"])')
        if not li:
            return None

        strong = li.select_one("strong")
        if not strong:
            return None

        text = (
            strong.get_text()
            .replace("$", "")
            .replace("/hr", "")
            .strip()
        )

        # Case: "$15 - $30"
        if "-" in text:
            try:
                low, high = text.split("-", 1)
                return {
                    "min": float(low.strip()),
                    "max": float(high.strip())
                }
            except ValueError:
                return None

        # Case: "$20"
        try:
            value = float(text)
            return {
                "min": value,
                "max": value
            }
        except ValueError:
            return None

    
    def fixed_budget(self) -> Optional[float]:
        li = self.soup.select_one('li:has(.description:contains("Fixed"))')
        if not li:
            return None

        strong = li.select_one("strong")
        if not strong:
            return None

        text = strong.get_text().replace("$", "").replace(",", "").strip()
        return float(text) if text.replace(".", "", 1).isdigit() else None

    def budget(self) -> Optional[dict]:
        job_type = self.job_type()

        if job_type == "fixed":
            amount = self.fixed_budget()
            if amount is None:
                return None
            return {
                "type": "fixed",
                "amount": amount
            }

        if job_type == "hourly":
            hourly = self.hourly_budget()
            if not hourly:
                return None
            return {
                "type": "hourly",
                "min": hourly["min"],
                "max": hourly["max"]
            }

        return None


    def experience_level(self) -> Optional[str]:
        el = self.soup.find("strong", string=re.compile("Entry|Intermediate|Expert"))
        return el.text.strip().lower() if el else None

    def skills(self) -> list[str]:
        return [
            self._clean(el.text)
            for el in self.soup.select('[data-test="Skill"] a')
            if el.text
        ]

    def client_activity(self) -> dict:  
        result = {}

        items = self.soup.select("ul.client-activity-items li.ca-item")
        for li in items:
            title_el = li.select_one(".title")
            value_el = li.select_one(".value")

            if not title_el or not value_el:
                continue

            key = (
                title_el.get_text()
                .replace(":", "")
                .strip()
                .lower()
                .replace(" ", "_")
            )

            value = value_el.get_text(strip=True)

            result[key] = value

        return result

    def job_link(self) -> Optional[str]:
        return f"https://www.upwork.com/jobs/~02{self.job_id()}"
    
    # --------------------
    # Client
    # --------------------

    def client_location(self) -> Optional[str]:
        try:
            location = self.soup.select_one('li[data-qa="client-location"] strong').text
            return  location if location else None
        except:
            return None
    
    def client_rating(self) -> Optional[str]:
        try:
            rating = self.soup.select_one('[data-testid="buyer-rating"]>span').text
            return rating if rating else None
        except: 
            return None
    
    def posted_jobs(self) -> Optional[str]:
        try:
            count = self.soup.select_one('[data-qa="client-job-posting-stats"] strong').text
            return self._clean(count) if count else None
        except:
            return None
    
    def hires_rating(self) -> Optional[str]:
        try:
            percent = self.soup.select_one('[data-qa="client-job-posting-stats"] div').text
            return self._clean(percent) if percent else None
        except: 
            return None
    def total_hires(self) -> Optional[str]:
        try:
            total = self.soup.select_one('[data-qa="client-hires"]').get_text(strip=True)
            return total if total else None
        except: 
            return None
    def total_spent(self) -> Optional[str]:
        try:
            total = self.soup.select_one('strong[data-qa="client-spend"]').get_text(strip=True)
            return total if total else None
        except: 
            return None
    def client_info(self) -> Optional[dict]:
        try:
            result = {
                "rating": self.client_rating() if self.client_rating() else 'N/A',
                "location": self.client_location() if self.client_location() else 'N/A',
                "posted_jobs": self.posted_jobs() if self.posted_jobs() else 'N/A',
                "hire_rate": self.hires_rating() if self.hires_rating() else 'N/A',
                "total_hires": self.total_hires() if self.total_hires() else 'N/A',
                "total_spent": self.total_spent() if self.total_spent() else 'N/A'
            }
            return result
        except Exception as e: 
            print(e)
        
        


    # --------------------
    # Export
    # --------------------
    def to_dict(self) -> dict:
        job_type = self.job_type()
        return {
            "job_id": self.job_id(),
            "title": self.title(),
            "posted_text": self.posted_time_text(),
            "posted_minutes_ago": self.posted_minutes_ago(),
            "location": self.location(),
            "description": self.description(),
            "job_type": self.job_type(),
            # giữ backward-compatible
            "hourly_budget": self.hourly_budget() if job_type == "hourly" else None,
            "fixed_budget": self.fixed_budget() if job_type == "fixed" else None,

            # chuẩn hoá – dùng cho notify / DB
            "budget": self.budget(),
            "experience_level": self.experience_level(),
            "skills": self.skills(),
            "activities": self.client_activity(),
            "url": self.job_link(),
            "client": self.client_info()
        }
