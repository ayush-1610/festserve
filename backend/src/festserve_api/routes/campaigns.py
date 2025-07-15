from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from sqlalchemy import func

from datetime import datetime

from festserve_api import models, schemas
from festserve_api.database import get_db
from festserve_api.auth import get_current_user

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

@router.post("/", response_model=schemas.CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: schemas.CampaignCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Ensure only advertisers can create
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Only advertisers may create campaigns")

    # Verify referenced stall and product exist
    stall = db.get(models.Stall, payload.stall_id)
    if not stall:
        raise HTTPException(status_code=404, detail="Stall not found")
    product = db.get(models.Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    campaign = models.Campaign(
        advertiser_id=current_user.advertiser_id,
        stall_id=payload.stall_id,
        product_id=payload.product_id,
        units_allocated=payload.units_allocated,
        start_datetime=payload.start_datetime,
        end_datetime=payload.end_datetime,
        status=models.CampaignStatus.scheduled,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign

@router.get("/", response_model=List[schemas.CampaignRead])
def list_campaigns(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Only advertisers may list campaigns")

    campaigns = (
        db.query(models.Campaign)
        .filter(models.Campaign.advertiser_id == current_user.advertiser_id)
        .all()
    )
    return campaigns

@router.get("/{campaign_id}", response_model=schemas.CampaignRead, status_code=status.HTTP_200_OK)
def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    campaign = db.get(models.Campaign, campaign_id)
    if not campaign or campaign.advertiser_id != current_user.advertiser_id:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

# ──────────────────────────────────────────────────────────────────────────────
# Reporting endpoints

@router.get(
    "/{campaign_id}/scans/count",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
def campaign_scan_count(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # only advertisers
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # verify campaign exists and belongs to this advertiser
    campaign = db.get(models.Campaign, campaign_id)
    if not campaign or campaign.advertiser_id != current_user.advertiser_id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    total = (
        db.query(func.count(models.ScanEvent.scan_event_id))
        .filter(models.ScanEvent.campaign_id == campaign_id)
        .scalar()
    )
    return {"campaign_id": campaign_id, "total_scans": total}

@router.get(
    "/{campaign_id}/scans",
    response_model=List[schemas.ScanEventRead],
    status_code=status.HTTP_200_OK,
)
def campaign_scan_list(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # only advertisers
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # verify campaign exists and belongs to this advertiser
    campaign = db.get(models.Campaign, campaign_id)
    if not campaign or campaign.advertiser_id != current_user.advertiser_id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    scans = (
        db.query(models.ScanEvent)
        .filter(models.ScanEvent.campaign_id == campaign_id)
        .all()
    )
    return scans

# ──────────────────────────────────────────────────────────────────────────────

@router.put(
    "/{campaign_id}",
    response_model=schemas.CampaignRead,
    status_code=status.HTTP_200_OK,
)
def update_campaign(
    campaign_id: UUID,
    payload: schemas.CampaignUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # only advertisers
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    campaign = db.get(models.Campaign, campaign_id)
    if not campaign or campaign.advertiser_id != current_user.advertiser_id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # apply any provided fields
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)
    return campaign

@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    campaign = db.get(models.Campaign, campaign_id)
    if not campaign or campaign.advertiser_id != current_user.advertiser_id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(campaign)
    db.commit()
    return

# ──────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{campaign_id}/snapshots",
    response_model=schemas.SnapshotRead,
    status_code=status.HTTP_201_CREATED,
)
def create_snapshot(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Only advertisers
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Verify ownership
    campaign = db.get(models.Campaign, campaign_id)
    if not campaign or campaign.advertiser_id != current_user.advertiser_id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Compute metrics
    total = (
        db.query(func.count(models.ScanEvent.scan_event_id))
        .filter(models.ScanEvent.campaign_id == campaign_id)
        .scalar()
    )
    remaining = campaign.units_allocated - total

    snapshot = models.ReportingSnapshot(
        campaign_id=campaign_id,
        snapshot_time=datetime.utcnow(),
        total_scans=total,
        remaining_units=remaining,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot

@router.get(
    "/{campaign_id}/snapshots",
    response_model=List[schemas.SnapshotRead],
    status_code=status.HTTP_200_OK,
)
def list_snapshots(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Only advertisers
    if not hasattr(current_user, "advertiser_id"):
        raise HTTPException(status_code=403, detail="Forbidden")

    campaign = db.get(models.Campaign, campaign_id)
    if not campaign or campaign.advertiser_id != current_user.advertiser_id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return (
        db.query(models.ReportingSnapshot)
        .filter(models.ReportingSnapshot.campaign_id == campaign_id)
        .order_by(models.ReportingSnapshot.snapshot_time.asc())
        .all()
    )
