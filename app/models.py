from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from .database import Base

enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)


def _now():
    return datetime.now(timezone.utc)


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=_now)
    contents = relationship("Content", back_populates="course", cascade="all, delete-orphan")
    students = relationship("Student", secondary=enrollments, back_populates="courses")


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    courses = relationship("Course", secondary=enrollments, back_populates="students")


class Content(Base):
    __tablename__ = "contents"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, default="")
    content_type = Column(String(20), default="text")  # text | video | pdf | quiz
    created_at = Column(DateTime(timezone=True), default=_now)
    course = relationship("Course", back_populates="contents")
