"""
FastAPI main application for Multi-Agent Job Applier
Compatible: FastAPI latest + CrewAI 1.9.3 + Groq Llama
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import traceback
from typing import List
from pathlib import Path

import docx2txt
import io
from PyPDF2 import PdfReader

# Models
from app.models.schemas import PipelineOutput, HealthResponse
from app.core.crew_runner import runner

# Create app instance
app = FastAPI(
    title="Multi-Agent Job Applier API 🚀",
    description="AI-powered job applications with resume parsing + Indeed scraping",
    version="2.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


# -----------------------------------------------------------
# Utility: extract text from PDF / DOCX / TXT
# -----------------------------------------------------------
def extract_resume_text(resume: UploadFile) -> str:
    content = resume.file.read()

    if resume.content_type == "text/plain":
        return content.decode("utf-8", errors="ignore")

    elif resume.content_type == "application/pdf":
        try:
            pdf_reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except:
            raise HTTPException(400, "Failed to extract text from PDF")

    elif resume.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            text = docx2txt.process(io.BytesIO(content))
            return text
        except:
            raise HTTPException(400, "Failed to extract text from DOCX")

    else:
        raise HTTPException(400, "Unsupported resume file format")


@app.post("/run_pipeline", response_model=PipelineOutput)
async def run_pipeline(
    job_query: str = Form(..., description="Job title/location (e.g. 'Machine Learning Engineer Hyderabad')"),
    resume: UploadFile = File(..., description="Resume file (PDF/DOCX/TXT)")
):
    """
    Complete job application pipeline:
    1. Scrape jobs
    2. Parse resume
    3. Skill gap analysis
    4. Generate tailored applications
    """
    try:
        # Validate file type
        allowed_types = [
            "text/plain",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
        if resume.content_type not in allowed_types:
            raise HTTPException(400, "Unsupported file type. Use PDF, TXT, or DOCX")

        # Extract usable text
        resume_text = extract_resume_text(resume)

        if len(resume_text.strip()) < 50:
            raise HTTPException(400, "Resume text is too short")

        # Run your pipeline
        result = runner.run_full_pipeline(
            resume_text=resume_text,
            job_query=job_query
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Pipeline error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Job Applier API 🚀",
        "endpoints": {
            "health": "/health",
            "pipeline": "/run_pipeline",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "usage": "POST /run_pipeline with job_query + resume file"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
