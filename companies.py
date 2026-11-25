"""Companies and job boards.

type "workday" / "greenhouse" / "smartrecruiters" / "amazon" -> fetched live
type "link"                                                    -> career-page link in the email
Tokens/tenants can change; failures are reported in the email footer, so fix or delete the entry.
"""

# ---- Live-fetched career sites (public JSON endpoints) ----
LIVE = [
    # Workday: tenant, wd (datacenter), site
    {"name": "Salesforce", "type": "workday", "tenant": "salesforce", "wd": "wd12", "site": "External_Career_Site"},
    {"name": "Adobe", "type": "workday", "tenant": "adobe", "wd": "wd5", "site": "external_experienced"},
    {"name": "NVIDIA", "type": "workday", "tenant": "nvidia", "wd": "wd5", "site": "NVIDIAExternalCareerSite"},
    {"name": "Dell", "type": "workday", "tenant": "dell", "wd": "wd1", "site": "External"},
    {"name": "Broadcom (VMware)", "type": "workday", "tenant": "broadcom", "wd": "wd1", "site": "External_Career"},
    {"name": "Mastercard", "type": "workday", "tenant": "mastercard", "wd": "wd1", "site": "CorporateCareers"},
    {"name": "Wells Fargo", "type": "workday", "tenant": "wf", "wd": "wd1", "site": "WellsFargoJobs"},
    {"name": "Thomson Reuters", "type": "workday", "tenant": "thomsonreuters", "wd": "wd5", "site": "External_Career_Site"},
    {"name": "Workday", "type": "workday", "tenant": "workday", "wd": "wd5", "site": "Workday"},
    {"name": "Intel", "type": "workday", "tenant": "intel", "wd": "wd1", "site": "External"},
    {"name": "Qualcomm", "type": "workday", "tenant": "qualcomm", "wd": "wd12", "site": "External"},
    {"name": "Micron", "type": "workday", "tenant": "micron", "wd": "wd1", "site": "External"},
    {"name": "HPE", "type": "workday", "tenant": "hpe", "wd": "wd5", "site": "Jobsathpe"},
    {"name": "Autodesk", "type": "workday", "tenant": "autodesk", "wd": "wd1", "site": "Ext"},
    {"name": "Walmart Global Tech", "type": "workday", "tenant": "walmart", "wd": "wd5", "site": "WalmartExternal"},
    {"name": "Red Hat", "type": "workday", "tenant": "redhat", "wd": "wd5", "site": "Jobs"},
    # Greenhouse: board token
    {"name": "Databricks", "type": "greenhouse", "token": "databricks"},
    {"name": "Stripe", "type": "greenhouse", "token": "stripe"},
    {"name": "Cloudflare", "type": "greenhouse", "token": "cloudflare"},
    {"name": "MongoDB", "type": "greenhouse", "token": "mongodb"},
    {"name": "Datadog", "type": "greenhouse", "token": "datadog"},
    {"name": "Okta", "type": "greenhouse", "token": "okta"},
    {"name": "Twilio", "type": "greenhouse", "token": "twilio"},
    # SmartRecruiters: company id
    {"name": "Visa", "type": "smartrecruiters", "company": "Visa"},
    # Custom JSON API
    {"name": "Amazon", "type": "amazon"},
]

# ---- Link-only (no usable public API): shown as search links in the email ----
LINKS = {
    "TCS": "https://www.tcs.com/careers",
    "Infosys": "https://www.infosys.com/careers/",
    "Wipro": "https://careers.wipro.com",
    "HCLTech": "https://www.hcltech.com/careers",
    "Tech Mahindra": "https://careers.techmahindra.com",
    "Cognizant": "https://careers.cognizant.com",
    "Accenture": "https://www.accenture.com/in-en/careers/jobsearch",
    "Capgemini": "https://www.capgemini.com/in-en/careers/",
    "IBM": "https://www.ibm.com/in-en/careers",
    "LTIMindtree": "https://www.ltimindtree.com/careers/",
    "Deloitte": "https://apply.deloitte.com",
    "EY": "https://www.ey.com/en_in/careers",
    "Microsoft": "https://careers.microsoft.com",
    "Google": "https://www.google.com/about/careers/applications/jobs/results/?location=Hyderabad",
    "Oracle": "https://careers.oracle.com",
    "Apple": "https://jobs.apple.com/en-in/search?location=hyderabad-HYB",
    "Cisco": "https://jobs.cisco.com",
    "SAP": "https://jobs.sap.com",
    "ServiceNow": "https://careers.servicenow.com",
    "Uber": "https://www.uber.com/in/en/careers/",
    "Flipkart": "https://www.flipkartcareers.com",
    "Zoho": "https://www.zoho.com/careers/",
    "Freshworks": "https://www.freshworks.com/company/careers/",
    "Atlassian": "https://www.atlassian.com/company/careers",
    "NetApp": "https://www.netapp.com/company/careers/",
    "Nutanix": "https://www.nutanix.com/company/careers",
    "Pure Storage": "https://www.purestorage.com/company/careers.html",
    "JPMorgan": "https://careers.jpmorgan.com",
    "Goldman Sachs": "https://www.goldmansachs.com/careers",
    "American Express": "https://www.americanexpress.com/en-in/careers/",
    "Honeywell": "https://careers.honeywell.com",
    "Infor": "https://www.infor.com/careers",
    "Persistent": "https://www.persistent.com/careers/",
    "Mphasis": "https://careers.mphasis.com",
    "Hexaware": "https://hexaware.com/careers/",
    "Virtusa": "https://www.virtusa.com/careers",
    "Genpact": "https://www.genpact.com/careers",
    "DXC": "https://careers.dxc.com",
    "NTT Data": "https://careers.nttdata.com",
    "Kyndryl": "https://www.kyndryl.com/in/en/careers",
}


def board_links(query):
    """Pre-filtered Hyderabad search links for the big job boards."""
    from urllib.parse import quote_plus as q
    s = q(query)
    return {
        "LinkedIn (last 24h)": f"https://www.linkedin.com/jobs/search/?keywords={s}&location=Hyderabad&f_TPR=r86400",
        "Indeed (last 24h)": f"https://in.indeed.com/jobs?q={s}&l=Hyderabad&fromage=1",
        "Naukri": f"https://www.naukri.com/{query.replace(' ', '-')}-jobs-in-hyderabad",
        "Foundit": f"https://www.foundit.in/srp/results?query={s}&locations=Hyderabad",
        "Glassdoor": f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={s}%20Hyderabad",
        "Instahyre": f"https://www.instahyre.com/search-jobs/?q={s}&location=Hyderabad",
        "Cutshort": f"https://cutshort.io/jobs?q={s}&location=Hyderabad",
    }
