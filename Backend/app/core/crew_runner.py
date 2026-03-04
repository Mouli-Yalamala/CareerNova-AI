"""
Pipeline Runner for CareerNova (CrewAI 1.9.3)
Orchestrates Research and Generation phases with a robust Match Guard.
"""

import time
import json
import traceback
import re
from datetime import datetime
from typing import Dict, Any

from app.core.crew_setup import CrewSetup
from app.models.schemas import (
    PipelineOutput,
    JobPosting,
    ResumeData,
    SkillGapAnalysis,
    ApplicationMaterials,
)

class PipelineRunner:
    def __init__(self):
        self.crew_setup = CrewSetup()

    def run_full_pipeline(self, resume_text: str, job_query: str, mock: bool = False) -> PipelineOutput:
        start_time = time.time()
        log_path = r"c:\Users\mouli\Documents\Job_explorer\Backend\pipeline_debug.log"
        
        try:
            # 1. Initialize Log
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n\n{'='*50}\n")
                f.write(f"PIPELINE START: {datetime.now()} {'(MOCK)' if mock else ''}\n")
                f.write(f"Query: {job_query}\n")
                f.flush()

            if mock:
                print("⚡ Returning MOCK DATA (No API Calls)...", flush=True)
                mock_jobs = [
                    JobPosting(job_title="Senior ML Engineer", company="CareerNova Tech", location="Hyderabad", url="http://example.com/1", description="Expert in AI"),
                    JobPosting(job_title="AI Researcher", company="Nova Labs", location="Remote", url="http://example.com/2", description="GenAI research")
                ]
                mock_resume = ResumeData(candidate_name="John Doe", summary="Experienced ML Dev", skills=["Python", "PyTorch"], experience=[], education=[])
                mock_gap = SkillGapAnalysis(match_score=85.0, missing_skills=["Docker"], strengths=["FastAPI"], roadmap=[], recommendation="Good candidate.", priority_jobs=["Senior ML Engineer"])
                mock_materials = ApplicationMaterials(tailored_resume="MOCK TAILORED RESUME", cover_letter="MOCK COVER LETTER", ats_score=85.0)
                
                return PipelineOutput(
                    job_scrapings=mock_jobs,
                    resume_data=mock_resume,
                    skill_gap_analysis=mock_gap,
                    application_materials=mock_materials,
                    execution_time=0.1,
                    success=True
                )

            print(f"🚀 Starting CareerNova Pipeline for: {job_query}", flush=True)

            # 2. Robust JSON Parser Utility
            def safe_parse_json(output_obj):
                """Extracts JSON from CrewOutput, dict, or raw strings with commentary."""
                if output_obj is None: return {}
                if isinstance(output_obj, (dict, list)): return output_obj
                
                raw_str = ""
                # CrewOutput has 'raw' or 'tasks_output'
                if hasattr(output_obj, 'json_dict') and output_obj.json_dict:
                    return output_obj.json_dict
                if hasattr(output_obj, 'raw'):
                    raw_str = str(output_obj.raw)  # Force string conversion
                elif isinstance(output_obj, str):
                    raw_str = output_obj
                
                if not raw_str or raw_str.lower() == "none": return {}

                # Sanitize invalid escapes (common in LLM output)
                # Replace \' with ' because \' is not valid JSON and agents often output it
                raw_str = raw_str.replace("\\'", "'")

                # Attempt direct parse
                try: return json.loads(raw_str)
                except: pass

                # Regex fallback for wrapped JSON
                try:
                    match = re.search(r'(\{.*\}|\[.*\])', raw_str, re.DOTALL)
                    if match: return json.loads(match.group(1))
                except: pass

                return {}

            # ----------------------------------------------------------
            # PHASE 1: RESEARCH (Agent 1, 2, 3)
            # ----------------------------------------------------------
            research_crew = self.crew_setup.create_research_crew()
            print("🔬 Phase 1: Research (Jobs, Resume Analysis, Skill Gap)...", flush=True)
            
            research_output = research_crew.kickoff(
                inputs={"job_query": job_query, "resume_text": resume_text}
            )
            
            outputs = research_output.tasks_output
            
            # Parse Outputs
            job_scraping_raw = safe_parse_json(outputs[0])
            
            # RESUME PARSING FALLBACK
            resume_raw = safe_parse_json(outputs[1])
            if not resume_raw or not isinstance(resume_raw, dict):
                print("⚠️ Resume Parsing returned empty/invalid data. Using fallback.", flush=True)
                resume_raw = {
                    "candidate_name": "Candidate",
                    "skills": ["Python"], 
                    "experience": [], 
                    "education": [], 
                    "total_years": 0, 
                    "summary": "Resume parsing failed - using placeholder."
                }

            gap_raw = safe_parse_json(outputs[2])

            # 3. Process Jobs (Improved to look for nested lists)
            job_postings = []
            
            # Identify if the list is nested under 'jobs', 'results', or 'job_postings'
            candidate_list = []
            if isinstance(job_scraping_raw, list):
                candidate_list = job_scraping_raw
            elif isinstance(job_scraping_raw, dict):
                # Look for common keys
                for key in ["jobs", "results", "job_postings", "listings"]:
                    if key in job_scraping_raw and isinstance(job_scraping_raw[key], list):
                        candidate_list = job_scraping_raw[key]
                        break
                if not candidate_list:
                    # If it's a single dict with job info, wrap it
                    if "job_title" in job_scraping_raw:
                        candidate_list = [job_scraping_raw]

            for j in candidate_list:
                if isinstance(j, dict) and "job_title" in j:
                    try: job_postings.append(JobPosting(**j))
                    except: pass

            if not job_postings:
                msg = f"No job postings could be parsed for query: {job_query}"
                print(f"⚠️ {msg} (Stopping Pipeline - No Jobs Found)", flush=True)
                
                # EARLY EXIT: No jobs found -> Stop pipeline
                return PipelineOutput(
                    job_scrapings=[],
                    execution_time=round(time.time() - start_time, 3),
                    success=True, # It's a valid result, just empty
                    error_message="No jobs found matching your query."
                )

            # 4. Extract Match Score (Match Guard)
            raw_score = gap_raw.get("match_score", gap_raw.get("overall_match_score", 0))
            try:
                if isinstance(raw_score, str):
                    match_score = float(str(raw_score).replace('%', '').strip())
                else:
                    match_score = float(raw_score)
            except:
                match_score = 0

            # Log Progress
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"Phase 1 Complete. Parsed Score: {match_score}%\n")
                f.write(f"Found {len(job_postings)} jobs.\n")
                f.flush()

            print(f"📊 Match Score: {match_score}%", flush=True)

            # ----------------------------------------------------------
            # PHASE 2: GENERATION (Agent 4)
            # ----------------------------------------------------------
            a_data = {}
            generation_skipped = False
            MATCH_THRESHOLD = 50.0

            if match_score >= MATCH_THRESHOLD:
                print(f"🎯 Score >= {MATCH_THRESHOLD}%. Proceeding to Generation Phase...", flush=True)
                gen_crew = self.crew_setup.create_generation_crew()
                
                inputs = {
                    "job_data": json.dumps(gap_raw.get("priority_jobs", job_scraping_raw)),
                    "resume_data": json.dumps(resume_raw)
                }
                
                # Removed gap_analysis to save tokens (Tool calculates it dynamically)
                print(f"📏 Gen Inputs Size: Job={len(inputs['job_data'])}, Resume={len(inputs['resume_data'])}", flush=True)

                # DEBUG LOGGING FOR GENERATION PHASE
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"\n--- GENERATION PHASE START ---\n")
                    f.write(f"Inputs Size: Job={len(inputs['job_data'])}, Resume={len(inputs['resume_data'])}\n")
                    f.flush()

                # Pass explicit strings to satisfy CrewAI input expectations
                gen_output = gen_crew.kickoff(inputs=inputs)

                # DEBUG LOGGING FOR GENERATION OUTPUT
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"\n--- GENERATION RAW OUTPUT ---\n")
                    # Handle CrewOutput or TaskOutput
                    raw_out = gen_output.tasks_output[0] if hasattr(gen_output, 'tasks_output') else str(gen_output)
                    f.write(str(raw_out))
                    f.write(f"\n-----------------------------\n")
                    f.flush()

                a_data = safe_parse_json(gen_output.tasks_output[0])
                
                # FIX: Unwrap if nested under 'application_generator_response'
                if "application_generator_response" in a_data:
                    print("📦 unwrapping nested 'application_generator_response'...", flush=True)
                    a_data = a_data["application_generator_response"]
                print("✅ Generation Phase: Complete.", flush=True)
            else:
                print(f"⚠️ Score < {MATCH_THRESHOLD}%. Skipping Generation to save credits.", flush=True)
                generation_skipped = True
                a_data = {
                    "tailored_resume": "NOT GENERATED: Match score below 50%. Focus on clearing the skill gap first.",
                    "cover_letter": "NOT GENERATED: Profile match is too weak.",
                    "ats_score": match_score,
                    "application_timestamp": datetime.now().isoformat(),
                    "recruiter_email": "",
                    "linkedin_message": "",
                    "keywords_used": [],
                    "recommended_jobs": []
                }

            # ----------------------------------------------------------
            # ASSEMBLE FINAL SCHEMA
            # ----------------------------------------------------------
            # Resume Data
            # Resume Data - Explicit sanitization for None values
            resume_raw.setdefault("candidate_name", "Candidate")
            resume_raw.setdefault("skills", [])
            
            if resume_raw.get("total_years") is None: resume_raw["total_years"] = 0
            if resume_raw.get("experience") is None: resume_raw["experience"] = []
            if resume_raw.get("education") is None: resume_raw["education"] = []
            if resume_raw.get("summary") is None: resume_raw["summary"] = "Profile summary not available."
            
            resume_data = ResumeData(**resume_raw)

            # Skill Gap
            skill_gap = SkillGapAnalysis(
                match_score=match_score,
                missing_skills=gap_raw.get("missing_skills", []),
                strengths=gap_raw.get("strengths", []),
                roadmap=gap_raw.get("roadmap", []),
                recommendation=gap_raw.get("recommendation", "N/A"),
                priority_jobs=gap_raw.get("priority_jobs", [])
            )

            # Application Materials - Explicit sanitization
            if a_data.get("tailored_resume") is None: a_data["tailored_resume"] = "Resume generation failed."
            if a_data.get("cover_letter") is None: a_data["cover_letter"] = "Cover letter generation failed."
            if a_data.get("recruiter_email") is None: a_data["recruiter_email"] = "Email generation failed."
            if a_data.get("linkedin_message") is None: a_data["linkedin_message"] = "Message generation failed."
            if a_data.get("keywords_used") is None: a_data["keywords_used"] = []
            if a_data.get("recommended_jobs") is None: a_data["recommended_jobs"] = []
            if a_data.get("ats_score") is None: a_data["ats_score"] = match_score
            
            a_data.setdefault("application_timestamp", datetime.now().isoformat())
            
            app_materials = ApplicationMaterials(**a_data)

            return PipelineOutput(
                job_scrapings=job_postings,
                resume_data=resume_data,
                skill_gap_analysis=skill_gap,
                application_materials=app_materials,
                execution_time=round(time.time() - start_time, 3),
                success=True,
                error_message="Skipped generation phase due to low match score." if generation_skipped else None
            )

        except Exception as e:
            err_trace = traceback.format_exc()
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\nCRITICAL ERROR: {str(e)}\n{err_trace}\n")
                f.flush()
            print(f"❌ Pipeline Failure: {e}", flush=True)
            return PipelineOutput(
                job_scrapings=[],
                execution_time=round(time.time() - start_time, 3),
                success=False,
                error_message=str(e)
            )

    async def run_single_task(self, task_name: str, inputs: Dict[str, Any]):
        raise RuntimeError("CrewAI 1.9.3 does not support running a single task directly")

runner = PipelineRunner()
