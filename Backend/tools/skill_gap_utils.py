"""
Advanced Skill Gap Analysis with fuzzy matching & learning roadmaps
Updated for CrewAI 1.9.3 BaseTool format WITHOUT losing any features.
"""

import json
import pandas as pd
from typing import List, Dict, Any, Tuple, Type
from Levenshtein import ratio
from crewai.tools import BaseTool
from pydantic import BaseModel
import re
from collections import Counter

# Learning resources database (India-focused)
LEARNING_RESOURCES = {
    'Python': {
        'free': [
            'https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU',
            'https://www.geeksforgeeks.org/python-programming-language/'
        ],
        'paid': ['https://www.udemy.com/course/complete-python-bootcamp/']
    },
    'FastAPI': {
        'free': [
            'https://fastapi.tiangolo.com/tutorial/',
            'https://www.youtube.com/watch?v=0sOvCWFmrtA'
        ],
        'paid': ['https://www.udemy.com/course/fastapi-the-complete-course/']
    },
    'Docker': {
        'free': [
            'https://www.docker.com/101-tutorial/',
            'https://www.youtube.com/playlist?list=PLhW3qGclg-I9p6w0byFV3J9YTxgJKgOaR'
        ],
        'paid': ['https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/']
    },
    'React': {
        'free': [
            'https://react.dev/learn',
            'https://www.youtube.com/playlist?list=PL4cUxeGkcC9gQeDH6xYhmO-db2mhoTSrT'
        ],
        'paid': ['https://www.udemy.com/course/react-the-complete-guide-incl-redux/']
    },
    'AWS': {
        'free': [
            'https://aws.amazon.com/training/free/',
            'https://www.youtube.com/playlist?list=PLv2aUT4Ms8nF4WpZ5XPW8wGMQYwD3ccM_'
        ],
        'paid': ['https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/']
    }
}

# --------------------------------------------------------
# 🔹 INPUT SCHEMA REQUIRED BY CREWAI 1.9.3
# --------------------------------------------------------
class SkillGapAnalyzerInput(BaseModel):
    job_data: str   # Expect PLAIN STRING, not JSON
    resume_data: str


# --------------------------------------------------------
# 🔥 MAIN TOOL CLASS — CrewAI 1.9.3 Compatible
# --------------------------------------------------------
class SkillGapAnalyzerTool(BaseTool):

    name: str = "skill_gap_analyzer"
    description: str = "Analyzes job vs resume skills using fuzzy matching and generates a learning roadmap."
    args_schema: Type[BaseModel] = SkillGapAnalyzerInput

    def _run(self, job_data: str, resume_data: str) -> str:
        """
        FIXED VERSION:
        - Does NOT expect JSON
        - Gracefully parses strings into skill lists
        - Keeps all your previous logic intact
        """

        # ---------------------------
        # 🔧 PARSE job_data SAFE
        # ---------------------------
        try:
            jobs = json.loads(job_data)  # REAL case (CrewAI pipeline)
        except:
            # FALLBACK when plain strings are passed (Swagger/manual tests)
            jobs = [{
                "skills_required": [s.strip() for s in job_data.split(",") if s.strip()],
                "job_title": "Unknown"
            }]

        # ---------------------------
        # 🔧 PARSE resume_data SAFE
        # ---------------------------
        try:
            resume = json.loads(resume_data)
            candidate_skills = [skill.lower() for skill in resume.get("skills", [])]
        except:
            candidate_skills = [s.strip().lower() for s in resume_data.split(",") if s.strip()]
            resume = {"skills": candidate_skills}

        # ---------------------------
        # BUILD job_skills
        # ---------------------------
        job_skills = []
        for job in jobs[:3]:
            job_skills.extend(job.get("skills_required", []))

        job_skills = list(set([skill.lower() for skill in job_skills]))

        # ---------------------------
        # 🧠 RUN ALL ORIGINAL LOGIC
        # ---------------------------
        match_results = analyze_skill_matches(job_skills, candidate_skills)
        match_score = calculate_match_score(match_results, len(job_skills))
        roadmap = generate_roadmap(match_results['missing'], job_skills)
        strengths = identify_strengths(match_results['matched'], job_skills, candidate_skills)

        result = {
            "match_score": round(match_score, 1),
            "total_job_skills": len(job_skills),
            "candidate_skills_matched": len(match_results['matched']),
            "missing_skills": match_results['missing'],
            "strengths": strengths,
            "roadmap": roadmap,
            "recommendation": get_recommendation(match_score),
            "priority_jobs": [job.get('job_title', "Unknown") for job in jobs[:2]]
        }

        return json.dumps(result, indent=2, ensure_ascii=False)

    async def _arun(self, job_data: str, resume_data: str) -> str:
        return self._run(job_data, resume_data)


# --------------------------------------------------------
# 🔍 HELPER LOGIC (unchanged)
# --------------------------------------------------------

def analyze_skill_matches(job_skills: List[str], candidate_skills: List[str]) -> Dict[str, List]:
    matched = []
    missing = []

    for job_skill in job_skills:
        best_match = None
        best_score = 0

        for cand_skill in candidate_skills:
            score = ratio(job_skill, cand_skill)
            if score > 0.85 and score > best_score:
                best_match = cand_skill
                best_score = score

        if best_match:
            matched.append({
                "job_skill": job_skill.title(),
                "candidate_skill": best_match.title(),
                "similarity": round(best_score * 100, 1)
            })
        else:
            missing.append(job_skill.title())

    return {"matched": matched, "missing": missing}


def calculate_match_score(match_results: Dict, total_job_skills: int) -> float:
    matched_count = len(match_results['matched'])
    core_multiplier = min(matched_count / total_job_skills * 1.5, 1.5)
    base_score = (matched_count / total_job_skills) * 100
    return min(base_score * core_multiplier, 100)


def generate_roadmap(missing_skills: List[str], all_job_skills: List[str]) -> List[Dict]:
    roadmap = []
    skill_priority = Counter(missing_skills)
    priority_skills = skill_priority.most_common(5)

    for i, (skill, freq) in enumerate(priority_skills):
        skill_lower = skill.lower()

        resources = LEARNING_RESOURCES.get(skill_lower.title(), {
            'free': [f"https://www.youtube.com/results?search_query={skill}+tutorial+india"],
            'paid': [f"https://www.udemy.com/courses/search/?q={skill}"]
        })

        roadmap.append({
            "step": i + 1,
            "skill": skill,
            "priority": "High" if i < 2 else "Medium",
            "estimated_hours": 20 if i == 0 else 15,
            "resources": {
                "free": resources['free'][:2],
                "paid": resources['paid'][:1],
                "youtube": f"https://www.youtube.com/results?search_query={skill}+tutorial+2026"
            },
            "why_important": f"Required in {freq} job postings"
        })

    return roadmap


def identify_strengths(matched_skills: List[Dict], job_skills: List[str], candidate_skills: List[str]) -> List[str]:
    strengths = []

    candidate_unique = set(candidate_skills) - set(job_skills)
    strengths.extend([skill.title() for skill in list(candidate_unique)[:3]])

    for match in matched_skills:
        if match['similarity'] > 95:
            strengths.append(f"Expertise in {match['candidate_skill']}")

    return strengths[:4]


def get_recommendation(match_score: float) -> str:
    if match_score >= 85:
        return "🟢 Excellent match! Apply immediately to all jobs."
    elif match_score >= 70:
        return "🟡 Good match. Learn 1-2 skills from roadmap, then apply."
    elif match_score >= 50:
        return "🟠 Fair match. Complete top 3 roadmap steps before applying."
    else:
        return "🔴 Poor match. Focus on roadmap before applying to these roles."
