from dotenv import load_dotenv
import os
from crewai import LLM

# --------------------------
# Disable ALL CrewAI memory & loops
# --------------------------
os.environ["CREWAI_DISABLE_MEMORY"] = "true"
os.environ["CREWAI_RAG_ENABLED"] = "false"
os.environ["CREWAI_USE_RAG"] = "false"

os.environ["CREWAI_AGENT_LOOP_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_REACT"] = "true"

os.environ["CREWAI_TOOL_RETRY"] = "false"
os.environ["CREWAI_TOOL_AUTO_RUN"] = "false"

load_dotenv()

default_llm = LLM(
    model="openrouter/google/gemini-2.0-flash-001",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.0,
    max_tokens=4000,
)