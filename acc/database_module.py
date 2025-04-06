
# database_module.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "interview_automation.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create companies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_email TEXT NOT NULL
                )
            """)
            
            # Create jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    requirements TEXT NOT NULL,
                    deadline DATETIME NOT NULL,
                    form_link TEXT UNIQUE NOT NULL,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # Create applicants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applicants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    resume_path TEXT NOT NULL,
                    score REAL,
                    FOREIGN KEY (job_id) REFERENCES jobs(id)
                )
            """)
            
            conn.commit()
    
    def _get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    # Company operations
    def create_company(self, name: str, contact_email: str) -> int:
        """Create a new company and return its ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO companies (name, contact_email) VALUES (?, ?)",
                (name, contact_email)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_company(self, company_id: int) -> Optional[Dict]:
        """Get company by ID"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # Job operations
    def create_job(self, company_id: int, title: str, description: str,
                 requirements: str, deadline: datetime, form_link: str) -> int:
        """Create a new job posting and return its ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO jobs 
                (company_id, title, description, requirements, deadline, form_link)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (company_id, title, description, requirements, deadline, form_link)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_job_by_form_link(self, form_link: str) -> Optional[Dict]:
        """Get job by its form link"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE form_link = ?", (form_link,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # Applicant operations
    def create_applicant(self, job_id: int, name: str, email: str, resume_path: str) -> int:
        """Create a new applicant and return its ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO applicants 
                (job_id, name, email, resume_path, score)
                VALUES (?, ?, ?, ?, NULL)""",
                (job_id, name, email, resume_path)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_applicant(self, applicant_id: int) -> Optional[Dict]:
        """Get applicant by ID"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_applicants_for_job(self, job_id: int) -> List[Dict]:
        """Get all applicants for a job"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applicants WHERE job_id = ?", (job_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_applicant_score(self, applicant_id: int, score: float):
        """Update an applicant's score"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE applicants SET score = ? WHERE id = ?",
                (score, applicant_id)
            )
            conn.commit()
    
    def are_applicants_processed(self, job_id: int) -> bool:
        """Check if all applicants for a job have been scored"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT COUNT(*) FROM applicants 
                WHERE job_id = ? AND score IS NULL""",
                (job_id,)
            )
            count = cursor.fetchone()[0]
            return count == 0
    
    def get_top_applicants(self, job_id: int, limit: int = 10) -> List[Dict]:
        """Get top scoring applicants for a job"""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM applicants 
                WHERE job_id = ? AND score IS NOT NULL
                ORDER BY score DESC
                LIMIT ?""",
                (job_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

# Singleton instance to be imported
db = Database()