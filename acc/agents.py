
# agents.py
from typing import List, Dict
from langchain.agents import AgentExecutor, Tool
from langchain.agents import initialize_agent
from langchain_community.llms import Ollama
from database_module import db

class ScoringAgent:
    def __init__(self):
        self.llm = Ollama(model="mistral")
        self.tools = self.load_tools()
        self.agent = self.create_agent()
    
    def load_tools(self) -> List[Tool]:
        """Load tools for the agent"""
        return [
            Tool(
                name="ResumeScorer",
                func=self.score_resume,
                description="Scores a resume against job requirements"
            ),
            Tool(
                name="DataFetcher",
                func=self.fetch_applicant_data,
                description="Fetches applicant data from database"
            )
        ]
    
    def create_agent(self) -> AgentExecutor:
        """Create the agent executor"""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=True
        )
    
    def process_job(self, job_id: int) -> List[Dict]:
        """Process all applicants for a job"""
        # Get all applicants for the job
        applicants = db.get_applicants_for_job(job_id)
        
        results = []
        for applicant in applicants:
            result = self.agent.run(
                f"Score applicant {applicant['id']} for job {job_id}"
            )
            results.append(result)
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:10]  # Top 10