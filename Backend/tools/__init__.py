"""CrewAI Tools Package"""
__version__ = "1.0.0"

# Auto-register tools for CrewAI
from .web_scraper import WebScraperTool
from .resume_parser import ResumeParserTool
from .skill_gap_utils import SkillGapAnalyzerTool
from .application_formatter import ApplicationFormatterTool
