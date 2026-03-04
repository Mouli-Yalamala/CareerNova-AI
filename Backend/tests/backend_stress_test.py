import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.crew_runner import runner

# Sample MOCK Data
MOCK_MARKETING_JOBS = json.dumps([
    {
        "job_title": "Digital Marketing Manager", 
        "company_name": "Creative Agency", 
        "skills_required": ["SEO", "Content Strategy", "Google Analytics"],
        "location": "Remote",
        "description": "Lead marketing campaigns.",
        "experience_years": 3,
        "url": "https://example.com/job1"
    }
])

MOCK_ZERO_JOBS = json.dumps([]) 

MOCK_RESUME = json.dumps({
    "candidate_name": "Marketer Doe",
    "skills": ["SEO", "Copywriting"],
    "experience": [],
    "education": [],
    "summary": "Experienced marketer."
})

class TestBackendStress(unittest.TestCase):

    @patch('tools.web_scraper.WebScraperTool._run')
    @patch('tools.resume_parser.ResumeParserTool._run')
    def test_non_tech_role(self, mock_parser, mock_scraper):
        print("\n🧪 TEST: Non-Tech Role (Digital Marketing)")
        # Setup Mocks
        mock_scraper.return_value = MOCK_MARKETING_JOBS
        mock_parser.return_value = MOCK_RESUME
        
        # Execute
        result = runner.run_full_pipeline(
            resume_text="Dummy resume text " * 50, 
            job_query="Digital Marketing"
        )
        
        # Assertions
        content = result.application_materials.cover_letter
        print(f"   [Debug Snippet]: {content[:80]}...")
        
        # Should not hallucinate Python if input is SEO
        self.assertIn("SEO", content)
        self.assertNotIn("FastAPI", content) 
        print("✅ PASS: Correctly adapted to Marketing role.")

    @patch('tools.web_scraper.WebScraperTool._run')
    @patch('tools.resume_parser.ResumeParserTool._run')
    def test_zero_results(self, mock_parser, mock_scraper):
        print("\n🧪 TEST: Zero Results Handling")
        # Setup Mocks
        mock_scraper.return_value = MOCK_ZERO_JOBS
        mock_parser.return_value = MOCK_RESUME
        
        # Execute
        result = runner.run_full_pipeline(
            resume_text="Dummy resume text", 
            job_query="GibberishQuery"
        )
        
        # Assertions
        # Should now FAIL gracefully with 0 jobs and an error message
        self.assertFalse(result.success)
        self.assertEqual(len(result.job_scrapings), 0)
        self.assertIsNotNone(result.error_message)
        print(f"✅ PASS: Pipeline stopped early with message: {result.error_message}")

    @patch('tools.web_scraper.WebScraperTool._run')
    @patch('tools.resume_parser.ResumeParserTool._run')
    def test_short_resume(self, mock_parser, mock_scraper):
        print("\n🧪 TEST: Short Resume Handling (Runner Level)")
        # Setup Mocks
        mock_scraper.return_value = MOCK_MARKETING_JOBS
        mock_parser.return_value = json.dumps({"candidate_name": "?", "skills": []})
        
        # Execute with tiny text
        try:
            result = runner.run_full_pipeline(
                resume_text="Too short", 
                job_query="Marketing"
            )
            self.assertTrue(result.success)
            print("✅ PASS: Pipeline did not crash on short text.")
        except Exception as e:
            self.fail(f"Pipeline crashed: {e}")

    @patch('app.core.crew_runner.PipelineRunner.run_full_pipeline')
    def test_low_match_score(self, mock_pipeline):
        print("\n🧪 TEST: Low Match Score Guard")
        from app.models.schemas import PipelineOutput, JobPosting, ResumeData, SkillGapAnalysis, ApplicationMaterials
        # Simulate a scenario where match score is 30%
        mock_pipeline.return_value = PipelineOutput(
            job_scrapings=[JobPosting(job_title="DevOps Engineer", company_name="TechCorp", skills_required=["Docker", "K8s", "Go"], location="Remote", description="Manage infra.", experience_years=5, url="https://example.com/job2")],
            resume_data=ResumeData(candidate_name="John Doe", summary="Web Dev", total_years=2, skills=["HTML", "CSS"], experience=[], education=[]),
            skill_gap_analysis=SkillGapAnalysis(match_score=30.0, missing_skills=["Docker", "K8s", "Go"], strengths=[], roadmap=[], recommendation="Low match", priority_jobs=["DevOps Engineer"]),
            application_materials=ApplicationMaterials(
                tailored_resume="NOT GENERATED: Match score below 50%.",
                cover_letter="NOT GENERATED.",
                recruiter_email="NOT GENERATED.",
                linkedin_message="NOT GENERATED.",
                ats_score=30.0,
                application_timestamp="2026-02-07",
                recommended_jobs=["DevOps Engineer"]
            ),
            execution_time=1.5,
            success=True,
            error_message="Generation skipped due to low match score (<50%)."
        )
        
        result = runner.run_full_pipeline("Resume", "DevOps")
        
        self.assertTrue(result.success)
        self.assertIn("NOT GENERATED", result.application_materials.tailored_resume)
        self.assertEqual(result.skill_gap_analysis.match_score, 30.0)
        print(f"✅ PASS: Generation skipped correctly. Message: {result.error_message}")

if __name__ == '__main__':
    unittest.main()
