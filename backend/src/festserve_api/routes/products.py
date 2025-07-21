from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from festserve_api import models, schemas
from festserve_api.database import get_db

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", response_model=schemas.ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
