"""
REAL-TIME Job scraping tool using SerpAPI (Indeed Scraper API)
Fully compatible with CrewAI 1.9.3
"""

from typing import List, Dict, Any, Type
from pydantic import BaseModel
from crewai.tools import BaseTool
import requests
import json
import os


# ------------------ INPUT SCHEMA ------------------ #
class WebScraperInput(BaseModel):
    job_query: str


# ------------------ TOOL CLASS ------------------ #
class WebScraperTool(BaseTool):
    name: str = "job_scraper"
    description: str = "Fetches 3–5 real job postings from Indeed India using SerpAPI."
    args_schema: Type[BaseModel] = WebScraperInput
    cache: bool = False 

    def _run(self, job_query: str) -> str:
        print("SCRAPER TOOL FILE USED:", os.path.abspath(__file__))
        print("🔧 DEBUG — Actual tool arg job_query =", job_query)
        api_key = os.getenv("SERPAPI_KEY")

        if not api_key:
            return json.dumps(
                {"error": "SERPAPI_KEY missing in environment"},
                indent=2
            )

        # SERPAPI Indeed endpoint
        url = "https://serpapi.com/search"

        params = {
            "engine": "google_jobs",   # SerpAPI job search
            "q": job_query,
            "hl": "en",
            "gl": "in",
            "api_key": api_key
        }

        try:
            print(f"🔍 Fetching REAL Indeed jobs for: {job_query}")

            response = requests.get(url, params=params, timeout=20)
            data = response.json()

            jobs_raw = data.get("jobs_results", [])[:5]

            jobs = []
            for job in jobs_raw:
                jobs.append({
                    "job_title": job.get("title"),
                    "company_name": job.get("company_name"),
                    "location": job.get("location"),
                    "salary_range": job.get("detected_extensions", {}).get("salary"),
                    "skills_required": job.get("job_highlights", {}).get("Qualifications", []),
                    "experience_years": 3,
                    "description": job.get("description"),
                    "url": job.get("apply_options", [{}])[0].get("link")
                })

            print(f"✅ Retrieved {len(jobs)} REAL jobs")
            return json.dumps(jobs, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"❌ SerpAPI scraping failed: {e}")
            return json.dumps([], indent=2)

    async def _arun(self, job_query: str) -> str:
        return self._run(job_query)
