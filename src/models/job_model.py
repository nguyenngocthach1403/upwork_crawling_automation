from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
import json
import csv


@dataclass
class Job:
    job_id: str
    title: str

    posted_text: Optional[str] = None
    posted_minutes_ago: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    budget: Optional[Dict[str, Any]] = None
    client: Optional[Dict[str, Any]] = None
    activities: Optional[Dict[str, Any]] = None

    url: Optional[str] = None

    # =====================================
    # 1️⃣ Convert to dict (Python native)
    # =====================================
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    # =====================================
    # 2️⃣ Convert to DB dict (JSON serialize dict fields)
    # =====================================
    def to_db_dict(self) -> Dict[str, Any]:
        data = asdict(self)

        # list -> string
        data["skills"] = ",".join(self.skills) if self.skills else None

        # dict -> json string
        for field_name in ["budget", "client", "activities"]:
            if data[field_name] is not None:
                data[field_name] = json.dumps(data[field_name], ensure_ascii=False)

        return data

    # =====================================
    # 3️⃣ Create from DB row
    # =====================================
    @classmethod
    def from_db_row(cls, row) -> "Job":

        skills = row["skills"].split(",") if row["skills"] else []
        activities = row["activities"].split(",") if row["activities"] else []

        budget = json.loads(row["budget"]) if row["budget"] else None

        return cls(
            job_id=row["job_id"],
            title=row["title"],
            posted_text=row["posted_text"],
            posted_minutes_ago=row["posted_minutes_ago"],
            location=row["location"],
            description=row["description"],
            job_type=row["job_type"],
            budget=budget,
            experience_level=row["experience_level"],
            skills=skills,
            activities=activities,
            client=row["client"],
            url=row["url"],
        )


    # =====================================
    # 4️⃣ Convert to CSV row
    # =====================================
    def to_csv_row(self) -> List[Any]:
        return [
            self.job_id,
            self.title,
            self.posted_text,
            self.posted_minutes_ago,
            self.location,
            self.description,
            self.job_type,
            self.experience_level,
            ",".join(self.skills),
            json.dumps(self.budget, ensure_ascii=False) if self.budget else "",
            json.dumps(self.client, ensure_ascii=False) if self.client else "",
            json.dumps(self.activities, ensure_ascii=False) if self.activities else "",
            self.url
        ]

    # =====================================
    # 5️⃣ Export list[Job] -> CSV
    # =====================================
    @staticmethod
    def export_to_csv(jobs: List["Job"], file_path: str) -> None:

        header = [
            "job_id", "title", "posted_text", "posted_minutes_ago",
            "location", "description", "job_type",
            "experience_level", "skills",
            "budget", "client", "activities", "url"
        ]

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for job in jobs:
                writer.writerow(job.to_csv_row())

    def budget_json(self):
        return json.dumps(self.budget) if self.budget else None

    def skills_json(self):
        return json.dumps(self.skills) if self.skills else None

    def activities_json(self):
        return json.dumps(self.activities) if self.activities else None

    def client_json(self):
        return json.dumps(self.client) if self.client else None

    def to_db_tuple(self, crawl_date: str):
        return (
            self.job_id,
            self.title,
            self.posted_text,
            self.posted_minutes_ago,
            self.location,
            self.description,
            self.job_type,
            json.dumps(self.budget) if self.budget else None,
            self.experience_level,
            json.dumps(self.skills) if self.skills else None,
            json.dumps(self.activities) if self.activities else None,
            json.dumps(self.client) if self.client else None,
            self.url,
            crawl_date
        )
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            job_id=data["job_id"],
            title=data["title"],
            posted_text=data["posted_text"],
            posted_minutes_ago=data["posted_minutes_ago"],
            location=data["location"],
            description=data["description"],
            job_type=data["job_type"],
            budget=data.get("budget", {}),
            experience_level=data.get("experience_level"),
            skills=data.get("skills", []),
            activities=data.get("activities", {}),
            client=data.get("client", {}),
            url=data["url"],
        )
