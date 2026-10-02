from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])


def _course_or_404(db: Session, course_id: int) -> models.Course:
    course = db.get(models.Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return course


@router.post("", response_model=schemas.CourseOut, status_code=201)
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db)):
    course = models.Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=List[schemas.CourseOut])
def list_courses(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.Course).offset(skip).limit(min(limit, 100)).all()


@router.get("/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    return _course_or_404(db, course_id)


@router.put("/{course_id}", response_model=schemas.CourseOut)
def update_course(course_id: int, payload: schemas.CourseCreate, db: Session = Depends(get_db)):
    course = _course_or_404(db, course_id)
    for k, v in payload.model_dump().items():
        setattr(course, k, v)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db.delete(_course_or_404(db, course_id))
    db.commit()


# ---- content (nested under course) ----
@router.post("/{course_id}/contents", response_model=schemas.ContentOut, status_code=201)
def add_content(course_id: int, payload: schemas.ContentCreate, db: Session = Depends(get_db)):
    _course_or_404(db, course_id)
    content = models.Content(course_id=course_id, **payload.model_dump())
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


@router.get("/{course_id}/contents", response_model=List[schemas.ContentOut])
def list_contents(course_id: int, db: Session = Depends(get_db)):
    return _course_or_404(db, course_id).contents


@router.delete("/{course_id}/contents/{content_id}", status_code=204)
def delete_content(course_id: int, content_id: int, db: Session = Depends(get_db)):
    content = db.get(models.Content, content_id)
    if not content or content.course_id != course_id:
        raise HTTPException(404, "Content not found")
    db.delete(content)
    db.commit()


@router.get("/{course_id}/students", response_model=List[schemas.StudentOut])
def course_students(course_id: int, db: Session = Depends(get_db)):
    return _course_or_404(db, course_id).students
