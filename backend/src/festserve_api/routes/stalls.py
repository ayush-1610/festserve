from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from festserve_api import models, schemas
from festserve_api.database import get_db

router = APIRouter(prefix="/api/stalls", tags=["stalls"])

@router.post("/", response_model=schemas.StallRead, status_code=status.HTTP_201_CREATED)
def create_stall(payload: schemas.StallCreate, db: Session = Depends(get_db)):
    stall = models.Stall(**payload.model_dump())
    db.add(stall)
    db.commit()
    db.refresh(stall)
    return stall
