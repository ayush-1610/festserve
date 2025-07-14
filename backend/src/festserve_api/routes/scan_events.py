from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from festserve_api import models, schemas
from festserve_api.database import get_db
from festserve_api.auth import get_current_user

router = APIRouter(prefix="/api/scan-events", tags=["scan-events"])

@router.post("/", response_model=schemas.ScanEventRead, status_code=status.HTTP_201_CREATED)
def create_scan_event(
    payload: schemas.ScanEventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Only scanner users can record scans
    if not hasattr(current_user, "user_id"):
        raise HTTPException(status_code=403, detail="Only scanner users may scan")

    # Verify the campaign exists
    campaign = db.get(models.Campaign, payload.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Create the scan event
    scan = models.ScanEvent(
        campaign_id=payload.campaign_id,
        scanner_user_id=current_user.user_id,
        device_fingerprint=payload.device_fingerprint,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan

@router.get("/", response_model=List[schemas.ScanEventRead])
def list_scan_events(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Only scanner users see their own scans
    if not hasattr(current_user, "user_id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    scans = (
        db.query(models.ScanEvent)
        .filter(models.ScanEvent.scanner_user_id == current_user.user_id)
        .all()
    )
    return scans
