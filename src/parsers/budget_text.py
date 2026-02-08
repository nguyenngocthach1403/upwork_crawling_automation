def budget_text(job: dict) -> str:
    b = job.get("budget")
    if not b:
        return "N/A"

    if b["type"] == "fixed":
        return f"Fixed: ${b['amount']:.2f}"

    if b["type"] == "hourly":
        return f"Hourly: ${b['min']:.2f} – ${b['max']:.2f}"

    return "N/A"
