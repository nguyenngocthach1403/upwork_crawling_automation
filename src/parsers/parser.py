from datetime import datetime, timedelta
import re

def parse_upwork_time(text: str):
    now = datetime.utcnow()

    if "hour" in text:
        n = int(re.search(r"\d+", text).group())
        return now - timedelta(hours=n)

    if "minute" in text:
        n = int(re.search(r"\d+", text).group())
        return now - timedelta(minutes=n)

    if "day" in text:
        n = int(re.search(r"\d+", text).group())
        return now - timedelta(days=n)

    if "yesterday" in text.lower():
        return now - timedelta(days=1)

    return None
