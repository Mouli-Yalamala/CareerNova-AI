"""
Pydantic models for API I/O - Compatible with FastAPI + Pydantic v2
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


# -------------------------------------------------
# JOB POSTING MODEL
# -------------------------------------------------
class JobPosting(BaseModel):
    job_title: str
    company_name: str
    location: str
    salary_range: Optional[str] = None
    skills_required: List[str]
    experience_years: int
    description: str
    url: str


# -------------------------------------------------
# RESUME ANALYSIS MODEL
# -------------------------------------------------
class ResumeData(BaseModel):
    candidate_name: str
    skills: List[str]
    total_years: int
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    summary: str


# -------------------------------------------------
# SKILL GAP ANALYSIS MODEL
# -------------------------------------------------
class SkillGapAnalysis(BaseModel):
    match_score: float
    missing_skills: List[str]
    strengths: List[str]
    roadmap: List[Dict[str, Any]]
    recommendation: Optional[str] = None
    priority_jobs: Optional[List[str]] = None


# -------------------------------------------------
# APPLICATION MATERIALS MODEL
# -------------------------------------------------
class ApplicationMaterials(BaseModel):
    tailored_resume: str
    cover_letter: str
    recruiter_email: str
    linkedin_message: str
    keywords_used: List[str]
    ats_score: float
    application_timestamp: str
    recommended_jobs: List[str]


# -------------------------------------------------
# PIPELINE INPUT (📥 REQUIRED by crew_runner)
# -------------------------------------------------
class PipelineInput(BaseModel):
    resume_text: str
    job_query: str


# -------------------------------------------------
# PIPELINE OUTPUT (📤 REQUIRED by crew_runner)
# -------------------------------------------------
class PipelineOutput(BaseModel):
    job_scrapings: List[JobPosting]
    resume_data: Optional[ResumeData] = None
    skill_gap_analysis: Optional[SkillGapAnalysis] = None
    application_materials: Optional[ApplicationMaterials] = None
    execution_time: float
    success: bool = True
    error_message: Optional[str] = None


# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = datetime.now()
