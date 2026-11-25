"""Job source connectors. Each returns a list of dicts:
id, title, company, location, desc, url, posted, source
"""
import os, re, time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (job-agent)"}
HYD = ("hyderabad", "telangana", "secunderabad", "hitec")


def is_hyd(text):
    t = (text or "").lower()
    return any(k in t for k in HYD)


def _clean(s):
    return re.sub(r"<[^>]+>", " ", s or "").strip()


# ---------------- Aggregators ----------------
def adzuna(queries):
    app_id, app_key = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")
    if not app_id:
        raise RuntimeError("ADZUNA keys not set")
    out = []
    for q in queries:
        for page in (1, 2):
            r = requests.get(
                f"https://api.adzuna.com/v1/api/jobs/in/search/{page}",
                params={"app_id": app_id, "app_key": app_key, "what": q, "where": "Hyderabad",
                        "distance": 30, "max_days_old": 3, "results_per_page": 50},
                timeout=30)
            r.raise_for_status()
            for j in r.json().get("results", []):
                out.append({"id": f"adzuna:{j['id']}", "title": _clean(j.get("title")),
                            "company": (j.get("company") or {}).get("display_name", ""),
                            "location": (j.get("location") or {}).get("display_name", ""),
                            "desc": _clean(j.get("description")), "url": j.get("redirect_url", ""),
                            "posted": (j.get("created") or "")[:10], "source": "Adzuna"})
            time.sleep(0.4)
    return out


def jsearch(queries):
    """JSearch (RapidAPI) aggregates LinkedIn, Indeed, Glassdoor, Naukri, Foundit etc. where available.
    Free tier is ~200 requests/month, so keep queries to ~5 per day."""
    key = os.environ.get("RAPIDAPI_KEY")
    if not key:
        raise RuntimeError("RAPIDAPI_KEY not set")
    out = []
    for q in queries:
        r = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers={"X-RapidAPI-Key": key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"},
            params={"query": f"{q} in Hyderabad, India", "page": "1", "num_pages": "1",
                    "country": "in", "date_posted": "3days"},
            timeout=40)
        r.raise_for_status()
        for j in r.json().get("data", []):
            loc = ", ".join(x for x in (j.get("job_city"), j.get("job_state")) if x)
            out.append({"id": f"jsearch:{j['job_id']}", "title": j.get("job_title", ""),
                        "company": j.get("employer_name", ""), "location": loc,
                        "desc": j.get("job_description", "")[:3000],
                        "url": j.get("job_apply_link", ""),
                        "posted": (j.get("job_posted_at_datetime_utc") or "")[:10],
                        "source": f"JSearch/{j.get('job_publisher', '')}"})
        time.sleep(0.5)
    return out


# ---------------- Direct career sites ----------------
def workday(c, max_pages=15):
    base = f"https://{c['tenant']}.{c['wd']}.myworkdayjobs.com"
    url = f"{base}/wday/cxs/{c['tenant']}/{c['site']}/jobs"
    out, offset = [], 0
    for _ in range(max_pages):
        r = requests.post(url, json={"appliedFacets": {}, "limit": 20, "offset": offset,
                                     "searchText": "Hyderabad"}, headers=HEADERS, timeout=30)
        r.raise_for_status()
        posts = r.json().get("jobPostings", [])
        if not posts:
            break
        for p in posts:
            path = p.get("externalPath", "")
            if is_hyd(p.get("locationsText")) or "hyderabad" in path.lower():
                out.append({"id": f"wd:{c['tenant']}:{path}", "title": p.get("title", ""),
                            "company": c["name"], "location": p.get("locationsText", "Hyderabad"),
                            "desc": "", "url": f"{base}/{c['site']}{path}",
                            "posted": p.get("postedOn", ""), "source": "Career site"})
        offset += 20
        time.sleep(0.3)
    return out


def greenhouse(c):
    r = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{c['token']}/jobs?content=true",
                     headers=HEADERS, timeout=40)
    r.raise_for_status()
    return [{"id": f"gh:{c['token']}:{j['id']}", "title": j.get("title", ""), "company": c["name"],
             "location": j["location"]["name"], "desc": _clean(j.get("content"))[:3000],
             "url": j.get("absolute_url", ""), "posted": (j.get("updated_at") or "")[:10],
             "source": "Career site"}
            for j in r.json().get("jobs", []) if is_hyd(j.get("location", {}).get("name"))]


def smartrecruiters(c):
    out = []
    r = requests.get(f"https://api.smartrecruiters.com/v1/companies/{c['company']}/postings",
                     params={"q": "Hyderabad", "limit": 100}, headers=HEADERS, timeout=30)
    r.raise_for_status()
    for j in r.json().get("content", []):
        loc = (j.get("location") or {})
        if is_hyd(loc.get("city")):
            out.append({"id": f"sr:{j['id']}", "title": j.get("name", ""), "company": c["name"],
                        "location": loc.get("city", ""), "desc": "",
                        "url": f"https://jobs.smartrecruiters.com/{c['company']}/{j['id']}",
                        "posted": (j.get("releasedDate") or "")[:10], "source": "Career site"})
    return out


def amazon(c):
    out = []
    for offset in (0, 100, 200):
        r = requests.get("https://www.amazon.jobs/en/search.json",
                         params={"loc_query": "Hyderabad, India", "country": "IND", "result_limit": 100,
                                 "offset": offset, "sort": "recent"}, headers=HEADERS, timeout=30)
        r.raise_for_status()
        jobs = r.json().get("jobs", [])
        for j in jobs:
            out.append({"id": f"amzn:{j['id_icims']}", "title": j.get("title", ""), "company": "Amazon",
                        "location": j.get("normalized_location", "Hyderabad"),
                        "desc": _clean(j.get("description_short")),
                        "url": "https://www.amazon.jobs" + j.get("job_path", ""),
                        "posted": j.get("posted_date", ""), "source": "Career site"})
        if len(jobs) < 100:
            break
    return out


CONNECTORS = {"workday": workday, "greenhouse": greenhouse,
              "smartrecruiters": smartrecruiters, "amazon": amazon}
