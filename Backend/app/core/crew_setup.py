"""
CrewAI agent/task loader with automatic JSON serialization and proper context passing.
Fully compatible with crewai==1.9.3
"""

import yaml
import sys
import json
from pathlib import Path
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process
from app.core.llm_config import default_llm

# Make tools importable
TOOLS_PATH = Path(__file__).parent.parent.parent / "tools"
sys.path.append(str(TOOLS_PATH))

from tools.web_scraper import WebScraperTool
from tools.resume_parser import ResumeParserTool
from tools.skill_gap_utils import SkillGapAnalyzerTool
from tools.application_formatter import ApplicationFormatterTool


class CrewSetup:
    def __init__(self):
        self.agents_path = Path(__file__).parent.parent / "config" / "agents.yaml"
        self.tasks_path = Path(__file__).parent.parent / "config" / "tasks.yaml"
        self.llm = default_llm

        self.tool_map = {
            "web_scraper.WebScraperTool": WebScraperTool,
            "resume_parser.ResumeParserTool": ResumeParserTool,
            "skill_gap_utils.SkillGapAnalyzerTool": SkillGapAnalyzerTool,
            "application_formatter.ApplicationFormatterTool": ApplicationFormatterTool
        }

    # ----------------------------------------------------------------------
    # LOAD AGENTS
    # ----------------------------------------------------------------------
    def load_agents(self) -> Dict[str, Agent]:
        with open(self.agents_path, "r", encoding="utf-8") as f:
            agents_config = yaml.safe_load(f)["agents"]

        agents_dict = {}

        for name, cfg in agents_config.items():

            tools = []
            for tool_name in cfg.get("tools", []):
                if tool_name in self.tool_map:
                    tools.append(self.tool_map[tool_name]())
            agent = Agent(
                role=cfg["role"],
                goal=cfg["goal"],
                backstory=cfg["backstory"],
                llm=self.llm,
                tools=tools,
                allow_delegation=False,
                verbose=False,
                memory=False,
                react_loop=False,
                max_iterations=2,
                disable_smart_mode=True,   # ← IMPORTANT
                max_loop=1,
                override_inputs = True
            )

            agents_dict[name] = agent
            print(f"✅ Loaded agent: {name}")

        return agents_dict

    # ----------------------------------------------------------------------
    # LOAD TASKS
    # ----------------------------------------------------------------------
    def load_tasks(self, agents_dict: Dict[str, Agent]) -> Dict[str, Task]:
        with open(self.tasks_path, "r", encoding="utf-8") as f:
            tasks_config = yaml.safe_load(f)["tasks"]

        tasks_dict = {}

        for name, cfg in tasks_config.items():

            task_tools = []
            for tool_name in cfg.get("tools", []):
                if tool_name in self.tool_map:
                    task_tools.append(self.tool_map[tool_name]())

            # NEW: automatic context passing
            task = Task(
                description=cfg["description"],
                expected_output=cfg["expected_output"],
                agent=agents_dict[cfg["agent"]],
                tools=task_tools,
                context=cfg.get("context", []), # ensures data flows forward
                override_agent_prompt=True,   # <-- CRITICAL FIX

            )

            tasks_dict[name] = task
            print(f"📝 Loaded task: {name}")

        return tasks_dict

    # ----------------------------------------------------------------------
    # BUILD CREWS (Phase-based for "Match Guard")
    # ----------------------------------------------------------------------
    def create_research_crew(self) -> Crew:
        """Runs Jobs + Resume + Gap Analysis (Tasks 1, 2, 3)"""
        agents = self.load_agents()
        tasks = self.load_tasks(agents)
        
        # MANUALLY LINK CONTEXT: Agent 3 needs output from Agent 1 (Jobs) AND Agent 2 (Resume)
        tasks["skill_gap_analysis_task"].context = [tasks["job_scraping_task"], tasks["resume_parsing_task"]]

        return Crew(
            agents=[agents["job_scraper_agent"], agents["resume_analyzer_agent"], agents["skill_gap_analyzer_agent"]],
            tasks=[tasks["job_scraping_task"], tasks["resume_parsing_task"], tasks["skill_gap_analysis_task"]],
            process=Process.sequential,
            verbose=True,
            memory=False
        )

    def create_generation_crew(self) -> Crew:
        """Runs Application Formatting (Task 4)"""
        agents = self.load_agents()
        tasks = self.load_tasks(agents)
        
        return Crew(
            agents=[agents["application_generator_agent"]],
            tasks=[tasks["application_generation_task"]],
            process=Process.sequential,
            verbose=True,
            memory=False
        )

    def create_crew(self) -> Crew:
        """Legacy method (Runs all 4)"""
        agents = self.load_agents()
        tasks = self.load_tasks(agents)

        # Ordered execution
        flow = [
            tasks["job_scraping_task"],
            tasks["resume_parsing_task"],
            tasks["skill_gap_analysis_task"],
            tasks["application_generation_task"]
        ]

        crew = Crew(
            agents=list(agents.values()),
            tasks=flow,
            process=Process.sequential,
            verbose=True,
            memory=False
        )

        return crew
