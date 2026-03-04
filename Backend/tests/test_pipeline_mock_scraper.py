import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.crew_runner import runner
from crewai.tools import BaseTool

# --------------------------------------------------------------------------------
# 1. Define the Mock Scraper (Returns data directly, no API calls)
# --------------------------------------------------------------------------------
class MockWebScraperTool(BaseTool):
    name: str = "job_scraper"
    description: str = "Returns verified mock job postings to bypass SerpAPI limits."

    def _run(self, job_query: str) -> str:
        print(f"\n🧪 [TEST MODE] MockScraper received query: {job_query}")
        print("🧪 [TEST MODE] Returning 2 hardcoded 'Machine Learning' jobs...")
        
        jobs = [
            {
                "job_title": "Machine Learning Engineer",
                "company_name": "FutureAI Systems",
                "location": "Hyderabad (Hybrid)",
                "salary_range": "₹15,00,000 - ₹25,00,000 a year",
                "skills_required": ["Python", "TensorFlow", "FastAPI", "NLP", "Docker"],
                "experience_years": 3,
                "description": """
                We are looking for a passionate Machine Learning Engineer to join our team in Hyderabad.
                You will design and deploy NLP models and build inference APIs using FastAPI.
                
                Responsibilities:
                - Build and optimize LLM pipelines.
                - Deploy models using Docker and Kubernetes.
                - Collaborate with backend teams to integrate AI features.
                
                Requirements:
                - 3+ years of experience in Python and ML.
                - Strong knowledge of Deep Learning (PyTorch/TensorFlow).
                - Experience with REST APIs (FastAPI/Flask).
                """,
                "url": "https://futureai.test/apply/1"
            },
            {
                "job_title": "AI Research Scientist",
                "company_name": "DeepTech Labs",
                "location": "Remote",
                "salary_range": "₹30,00,000 - ₹45,00,000 a year",
                "skills_required": ["Python", "PyTorch", "Generative AI", "RAG"],
                "experience_years": 5,
                "description": "Lead research on Generative AI and RAG systems.",
                "url": "https://deeptech.test/apply/2"
            }
        ]
        return json.dumps(jobs, indent=2)

# --------------------------------------------------------------------------------
# 2. Inject the Mock Tool into the existing Runner
# --------------------------------------------------------------------------------
print("🛠️  Patching PipelineRunner with MockWebScraperTool...")

# We replace the class in the tool_map. 
# When 'create_research_crew' is called, it will instantiate OUR tool instead of the real one.
runner.crew_setup.tool_map["web_scraper.WebScraperTool"] = MockWebScraperTool

# --------------------------------------------------------------------------------
# 3. Run the Pipeline
# --------------------------------------------------------------------------------
print("🚀 Starting Pipeline Test (Real LLMs + Mock Scraper)...")

resume_text = """
John Doe
Python Developer | ML Enthusiast
Hyderabad, India

Summary:
Skilled Python Developer with 4 years of experience in building scalable web APIs and 
experimenting with Machine Learning models. Passionate about AI agents and automation.

Skills:
- Languages: Python, JavaScript, SQL
- Frameworks: FastAPI, Django, Flask
- AI/ML: Basic TensorFlow, LangChain, OpenAI API
- Tools: Git, Docker, Postman

Experience:
Software Engineer | TechCorp | 2021 - Present
- Built microservices using FastAPI handling 10k+ req/day.
- integrated OpenAI API for chatbot feature.
- Optimized database queries reducing load times by 40%.

Education:
B.Tech Computer Science | JNTU Hyderabad | 2017 - 2021
"""

try:
    result = runner.run_full_pipeline(
        resume_text=resume_text,
        job_query="Machine Learning Engineer Hyderabad"
    )

    print("\n" + "="*50)
    if result.success:
        print("✅ TEST PASSED!")
        print(f"⏱️  Execution Time: {result.execution_time}s")
        print(f"📊 Match Score: {result.skill_gap_analysis.match_score}%")
        print(f"📝 Jobs Found: {len(result.job_scrapings)}")
        
        if result.application_materials:
            print("\n📄 GENERATED MATERIALS:")
            print(f"   - Resume Sentences: {len(result.application_materials.tailored_resume.split('.'))}")
            print(f"   - Cover Letter Len: {len(result.application_materials.cover_letter)} chars")
            print(f"   - Recruiter Email: {'Yes' if result.application_materials.recruiter_email else 'No'}")
        else:
            print("⚠️  No application materials generated (Match Score might be too low).")
            
    else:
        print(f"❌ TEST FAILED: {result.error_message}")

except Exception as e:
    import traceback
    traceback.print_exc()
