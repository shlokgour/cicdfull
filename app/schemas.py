from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""


class CourseOut(ORM):
    id: int
    title: str
    description: str
    created_at: datetime


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class StudentOut(ORM):
    id: int
    name: str
    email: str
    created_at: datetime


class ContentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = ""
    content_type: Literal["text", "video", "pdf", "quiz"] = "text"


class ContentOut(ORM):
    id: int
    course_id: int
    title: str
    body: str
    content_type: str
    created_at: datetime


class StudentWithCourses(StudentOut):
    courses: List[CourseOut] = []
