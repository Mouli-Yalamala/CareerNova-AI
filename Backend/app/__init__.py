"""Multi-Agent Job Application System - Main Package"""
__version__ = "1.0.0"
__author__ = "AI Engineer"

# Auto-import for clean imports
from app.models.schemas import (
    PipelineInput,
    PipelineOutput,
    HealthResponse
)
from .core.crew_runner import runner
