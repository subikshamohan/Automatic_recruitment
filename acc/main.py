
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uuid
import json  # <-- Added missing import
from typing import Optional
import asyncio

app = FastAPI()

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"  # Or any model you prefer

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
jobs_db = {}
applications_db = {}

async def analyze_with_ollama(job_id: str, application_id: str):
    job = jobs_db[job_id]
    application = applications_db[application_id]
    
    # In production, you would extract text from the resume file here
    # For this example, we'll use a placeholder
    resume_text = "Extracted resume text would appear here"
    
    prompt = f"""
    Analyze this job application and provide a matching score between 0-100.
    
    Job Title: {job['title']}
    Job Description: {job['description']}
    Key Requirements: {job['requirements']}
    
    Applicant: {application['name']}
    Cover Letter: {application['cover_letter']}
    Resume Summary: {resume_text}
    
    Provide your response in this exact JSON format:
    {{
        "score": 0-100,
        "strengths": ["list", "of", "strengths"],
        "improvements": ["list", "of", "improvements"],
        "summary": "brief overall assessment"
    }}
    """
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            analysis = result.get("response", "{}")
            
            try:
                # Validate the JSON response
                parsed_analysis = json.loads(analysis)
                return parsed_analysis
            except json.JSONDecodeError:
                return {
                    "error": "Invalid JSON response from AI",
                    "raw_response": analysis
                }
            
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/jobs")
async def create_job(
    title: str = Form(...),
    description: str = Form(...),
    requirements: str = Form(...)
):
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {
        "title": title,
        "description": description,
        "requirements": requirements
    }
    return {
        "job_id": job_id,
        "form_link": f"http://localhost:8000/apply/{job_id}"
    }

@app.post("/api/applications")
async def submit_application(
    name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    job_id: str = Form(...),
    cover_letter: Optional[str] = Form(None)
):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Save resume (in production, you'd extract text here)
    file_ext = os.path.splitext(resume.filename)[1]
    resume_filename = f"{uuid.uuid4()}{file_ext}"
    resume_path = os.path.join("uploads", resume_filename)
    os.makedirs("uploads", exist_ok=True)
    
    with open(resume_path, "wb") as f:
        f.write(await resume.read())
    
    # Store application
    application_id = str(uuid.uuid4())
    applications_db[application_id] = {
        "job_id": job_id,
        "name": name,
        "email": email,
        "resume_path": resume_path,
        "cover_letter": cover_letter,
        "status": "received"
    }
    
    # Start AI analysis in background
    analysis_result = await analyze_with_ollama(job_id, application_id)
    applications_db[application_id]["analysis"] = analysis_result
    applications_db[application_id]["status"] = "complete"
    
    return {
        "application_id": application_id,
        "status": "analysis_complete",
        "analysis": analysis_result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)