
# matching.py
import ollama
from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from database_module import db

class ResumeMatcher:
    def __init__(self):
        self.embedding_model = "nomic-embed-text"  # Ollama embedding model
        
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Ollama"""
        response = ollama.embeddings(model=self.embedding_model, prompt=text)
        return response['embedding']
    
    def calculate_similarity(self, job_desc: str, resume_text: str) -> float:
        """Calculate similarity score between job description and resume"""
        job_embedding = self.get_embedding(job_desc)
        resume_embedding = self.get_embedding(resume_text)
        
        # Convert to numpy arrays and reshape for cosine similarity
        job_arr = np.array(job_embedding).reshape(1, -1)
        resume_arr = np.array(resume_embedding).reshape(1, -1)
        
        similarity = cosine_similarity(job_arr, resume_arr)[0][0]
        return round(similarity * 100, 2)  # Convert to percentage
    
    def extract_resume_text(self, resume_path: str) -> str:
        """Extract text from resume (PDF/DOCX)"""
        # Implement using python-docx, PyPDF2, or other libraries
        pass
    
    def score_applicant(self, job_id: int, applicant_id: int) -> Dict:
        """Score a single applicant against job requirements"""
        # Get job and applicant from database
        job = db.get_job(job_id)
        applicant = db.get_applicant(applicant_id)
        
        # Extract text from resume
        resume_text = self.extract_resume_text(applicant.resume_path)
        
        # Combine job description and requirements
        job_text = f"{job.description}\n\nRequirements:\n{job.requirements}"
        
        # Calculate similarity score
        score = self.calculate_similarity(job_text, resume_text)
        
        # Update applicant score in database
        db.update_applicant_score(applicant_id, score)
        
        return {"applicant_id": applicant_id, "score": score}