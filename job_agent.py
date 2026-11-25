"""Daily Hyderabad job agent for Sai Krishna Devara.

Sources: Adzuna, JSearch (LinkedIn/Indeed/Glassdoor/etc. via RapidAPI), direct career sites
(Workday/Greenhouse/SmartRecruiters/Amazon). Scores against your CV profile, dedupes, skips
already-seen jobs, and emails the full list + CSV, with search links for boards/companies
that have no public API (Naukri, Foundit, Glassdoor, TCS, Infosys, ...).

Env: ADZUNA_APP_ID, ADZUNA_APP_KEY, RAPIDAPI_KEY, SMTP_USER, SMTP_PASS, MAIL_TO
"""
import csv, html, json, os, smtplib, ssl
from datetime import date
from email.message import EmailMessage
from pathlib import Path

import sources
from companies import LIVE, LINKS, board_links

QUERIES = [
    "cloud infrastructure manager",
    "technical product owner infrastructure",
    "senior service delivery manager",
    "cloud transformation manager",
    "platform engineering manager",
    "devops manager",
    "cloud program manager",
    "infrastructure operations manager",
]
JSEARCH_QUERIES = QUERIES[:5]  # free tier is ~200 requests/month; 5/day = 150

SKILLS = {
    "cloud": 3, "infrastructure": 3, "product owner": 4, "service delivery": 4,
    "transformation": 3, "platform engineering": 3, "devops": 2, "aws": 2, "azure": 2,
    "openstack": 3, "vmware": 2, "kubernetes": 2, "ansible": 1, "finops": 3, "itil": 2,
    "servicenow": 2, "agile": 1, "migration": 2, "linux": 1, "capacity planning": 1,
    "incident management": 1, "aiops": 2, "roadmap": 2, "backlog": 1, "sre": 1,
    "site reliability": 2, "operations": 1, "delivery": 1,
}
SENIOR = ["manager", "lead", "head", "director", "principal", "product owner", "architect", "senior", "staff"]
JUNIOR = ["intern", "trainee", "fresher", "junior", "associate engineer", "graduate"]
MIN_SCORE = 8          # when a description is available
MIN_SCORE_TITLE = 6    # title-only sources (Workday, SmartRecruiters)
EMAIL_MAX = 150
SEEN_FILE, OUT_DIR = Path("seen_jobs.json"), Path("output")


def score(j):
    title = j["title"].lower()
    text = (title + " " + j["desc"]).lower()
    s, hits = 0, []
    for kw, w in SKILLS.items():
        if kw in text:
            s += w * (2 if kw in title else 1)
            hits.append(kw)
    if any(t in title for t in SENIOR):
        s += 4
    if any(t in title for t in JUNIOR):
        s -= 15
    return s, hits


def collect():
    jobs, status = [], []

    def run(name, fn, *args):
        try:
            res = fn(*args)
            jobs.extend(res)
            status.append((name, len(res), None))
        except Exception as e:  # one bad source must not kill the run
            status.append((name, 0, str(e)[:80]))

    run("Adzuna", sources.adzuna, QUERIES)
    run("JSearch", sources.jsearch, JSEARCH_QUERIES)
    for c in LIVE:
        run(c["name"], sources.CONNECTORS[c["type"]], c)
    return jobs, status


def main():
    seen = set(json.loads(SEEN_FILE.read_text())) if SEEN_FILE.exists() else set()
    raw, status = collect()
    found = {}
    for j in raw:
        if not sources.is_hyd(j["location"]):
            continue
        key = (j["title"].lower().strip(), j["company"].lower().strip())
        if j["id"] in seen or key in found:
            continue
        j["score"], j["why"] = score(j)
        need = MIN_SCORE if len(j["desc"]) > 200 else MIN_SCORE_TITLE
        if j["score"] >= need:
            found[key] = j
    jobs = sorted(found.values(), key=lambda x: -x["score"])

    OUT_DIR.mkdir(exist_ok=True)
    csv_path = OUT_DIR / f"jobs_{date.today()}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Score", "Title", "Company", "Location", "Posted", "Source", "Matched on", "Link"])
        for j in jobs:
            w.writerow([j["score"], j["title"], j["company"], j["location"], j["posted"],
                        j["source"], ", ".join(j["why"]), j["url"]])
    SEEN_FILE.write_text(json.dumps(sorted(seen | {j["id"] for j in raw if j["id"]})))
    print(f"{len(jobs)} new matching jobs -> {csv_path}")
    for s in status:
        print("  ", s)
    send_email(jobs, status, csv_path)


def build_html(jobs, status):
    h = [f"<h2>{len(jobs)} new Hyderabad jobs matching your CV ({date.today()})</h2>"]
    for i, j in enumerate(jobs[:EMAIL_MAX], 1):
        h.append(f"<p><b>{i}. <a href='{html.escape(j['url'])}'>{html.escape(j['title'])}</a></b> "
                 f"- {html.escape(j['company'])}<br><small>Match {j['score']} | {html.escape(j['source'])} | "
                 f"{html.escape(j['posted'])} | {html.escape(', '.join(j['why'][:6]))}</small></p>")
    if len(jobs) > EMAIL_MAX:
        h.append(f"<p>+{len(jobs) - EMAIL_MAX} more in the attached CSV.</p>")
    h.append("<h3>Search these boards now (pre-filtered for Hyderabad)</h3><p>")
    h.append(" | ".join(f"<a href='{u}'>{n}</a>" for n, u in board_links(QUERIES[0]).items()))
    h.append("</p><h3>Company career pages</h3><p>")
    h.append(" | ".join(f"<a href='{u}'>{n}</a>" for n, u in LINKS.items()))
    h.append("</p><hr><small>Sources: " + "; ".join(
        f"{n}: {c}" if not e else f"{n}: FAILED ({html.escape(e)})" for n, c, e in status) + "</small>")
    return "\n".join(h)


def send_email(jobs, status, csv_path):
    if not os.environ.get("SMTP_USER"):
        return
    msg = EmailMessage()
    msg["Subject"] = f"Hyderabad jobs for you: {len(jobs)} new ({date.today()})"
    msg["From"], msg["To"] = os.environ["SMTP_USER"], os.environ["MAIL_TO"]
    msg.set_content("Open this email in an HTML-capable client. Full list is in the attached CSV.")
    msg.add_alternative(build_html(jobs, status), subtype="html")
    msg.add_attachment(csv_path.read_bytes(), maintype="text", subtype="csv", filename=csv_path.name)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        s.send_message(msg)


if __name__ == "__main__":
    main()
