from .budget_text import budget_text

def format_job_message(job: dict) -> str:
    return f"""
🚀 <b>{job['title']}</b>

🕒 <b>Posted:</b> {job.get('posted_text', 'N/A')}
💰 <b>Budget:</b> {budget_text(job)}
🛠 <b>Skills:</b> {", ".join(job.get('skills', []))}
⭐ <b>Preferred:</b>
📍 <b>Location:</b> {job.get('location', 'Worldwide')}
📊 <b>Proposals:</b> {dict(job.get('activities')).get('proposals', "N/A")}
⚡ <b>Invites sent:</b> {dict(job.get('activities')).get('invites_sent', "N/A")}

👤 <b>About Client</b>👤
    <b>Rating:</b> {dict(job.get('client')).get('rating', "N/A")}
📈  <b>Hire rate:</b> {dict(job.get('client')).get('hire_rate', "N/A")}
    <b>Posted Jobs:</b> {dict(job.get('client')).get('posted_jobs', "N/A")}

🔗 <b>Link:</b>
{job['url']}
""".strip()

# 👤 <b>Client:</b> {job.get('client_rating', 'N/A')}
# 📈 <b>Hire Rate:</b> {job.get('hire_rate', 'N/A')}