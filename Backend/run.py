#!/usr/bin/env python3
"""
Production launcher for Multi-Agent Job Applier
"""
import os
import sys
from pathlib import Path
import uvicorn

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from app.api.main import app
from app.core.crew_runner import runner
import warnings

# Suppress Pydantic V2 migration warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
try:
    from pydantic import PydanticDeprecatedSince20
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
except ImportError:
    pass

def main():
    """CLI entrypoint"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent Job Application System")
    parser.add_argument("--dev", action="store_true", help="Development mode with reload")
    parser.add_argument("--test", action="store_true", help="Run pipeline test")
    parser.add_argument("--mock", action="store_true", help="Run with mock data (no LLM usage)")
    args = parser.parse_args()

    if args.mock:
        print("🧪 Running in MOCK mode (No LLM usage)...")
        from app.core.crew_runner import runner
        # We'll modify runner to handle this
        result = runner.run_full_pipeline(
            resume_text="Mock Resume Text",
            job_query="Mock Job Query",
            mock=True
        )
        print("✅ Mock run complete.")
        print(f"📊 Result Success: {result.success}")
        return
    
    if args.test:
        print("🧪 Testing pipeline...")
        from app.core.crew_runner import runner
        result = runner.run_full_pipeline(
            resume_text="John Doe, Python FastAPI 5 years B.Tech VIT",
            job_query="Machine learning engineer hyderabad"
        )
        if result.success:
            print(f"✅ Test successful! Time: {result.execution_time}s")
            print(f"📊 Match Score: {result.skill_gap_analysis.match_score}%")
            if result.application_materials.tailored_resume != "Generation failed.":
                print("📝 Generation Phase: SUCCESS")
            else:
                print("⚠️ Generation Phase: FAILED/SKIPPED")
        else:
            print(f"❌ Test failed: {result.error_message}")
        return
    
    # Launch FastAPI server
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "run:app",
        host=host,
        port=port,
        reload=args.dev,
        log_level="info" if not args.dev else "debug"
    )

if __name__ == "__main__":
    main()
