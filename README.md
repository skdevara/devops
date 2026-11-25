# Hyderabad Job Agent

Runs daily at 8:00 AM IST, finds new Hyderabad jobs matching your CV, emails the full list (plus CSV).

## Setup (about 10 minutes)
1. Get free Adzuna API keys: https://developer.adzuna.com
2. Create a private GitHub repo and upload everything in this folder.
3. Gmail: turn on 2-step verification, then create an App Password.
4. Repo > Settings > Secrets and variables > Actions, add:
   ADZUNA_APP_ID, ADZUNA_APP_KEY, SMTP_USER (your Gmail), SMTP_PASS (app password), MAIL_TO
5. Repo > Actions > "Daily Hyderabad Jobs" > Run workflow to test.

## Tuning
Edit QUERIES, SKILLS, MIN_SCORE at the top of job_agent.py.
Lower MIN_SCORE for more results, raise it for tighter matches.

## Added: JSearch + direct career sites
- JSearch (RapidAPI, free tier ~200 requests/month): https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch . Add the key as secret RAPIDAPI_KEY. It pulls LinkedIn, Indeed, Glassdoor and others where available.
- Live career-site connectors (companies.py > LIVE): Workday, Greenhouse, SmartRecruiters, Amazon. Tenants can change; failures show in the email footer.
- Naukri, Foundit, Glassdoor, Instahyre, Cutshort and TCS/Infosys/Wipro etc. have no public API and block scraping, so the email carries pre-filtered Hyderabad search links for them.
- To add a company: append an entry to LIVE (Workday/Greenhouse) or LINKS.
