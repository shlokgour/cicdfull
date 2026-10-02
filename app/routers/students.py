from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/students", tags=["students"])


def _student_or_404(db: Session, student_id: int) -> models.Student:
    student = db.get(models.Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    return student


@router.post("", response_model=schemas.StudentOut, status_code=201)
def create_student(payload: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered")
    db.refresh(student)
    return student


@router.get("", response_model=List[schemas.StudentOut])
def list_students(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.Student).offset(skip).limit(min(limit, 100)).all()


@router.get("/{student_id}", response_model=schemas.StudentWithCourses)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return _student_or_404(db, student_id)


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db.delete(_student_or_404(db, student_id))
    db.commit()


@router.post("/{student_id}/enroll/{course_id}", status_code=204)
def enroll(student_id: int, course_id: int, db: Session = Depends(get_db)):
    student = _student_or_404(db, student_id)
    course = db.get(models.Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    if course not in student.courses:
        student.courses.append(course)
        db.commit()
