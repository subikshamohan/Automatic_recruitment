
# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact_email = Column(String)
    jobs = relationship("Job", back_populates="company")

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    title = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    deadline = Column(DateTime)
    form_link = Column(String)  # Unique generated link
    company = relationship("Company", back_populates="jobs")
    applicants = relationship("Applicant", back_populates="job")

class Applicant(Base):
    __tablename__ = 'applicants'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    name = Column(String)
    email = Column(String)
    resume_path = Column(String)  # Path to uploaded resume
    score = Column(Integer)  # AI-generated matching score
    job = relationship("Job", back_populates="applicants")