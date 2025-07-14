# festserve_api/tasks.py

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from festserve_api.database import SessionLocal
from festserve_api import models

def snapshot_all_campaigns() -> None:
    """
    For every campaign in the DB, record a ReportingSnapshot
    with the current total scans and remaining units.
    """
    db: Session = SessionLocal()
    try:
        campaigns = db.query(models.Campaign).all()
        for campaign in campaigns:
            total = (
                db.query(func.count(models.ScanEvent.scan_event_id))
                .filter(models.ScanEvent.campaign_id == campaign.campaign_id)
                .scalar() or 0
            )
            remaining = campaign.units_allocated - total
            snap = models.ReportingSnapshot(
                campaign_id=campaign.campaign_id,
                snapshot_time=datetime.utcnow(),
                total_scans=total,
                remaining_units=remaining,
            )
            db.add(snap)
        db.commit()
    finally:
        db.close()
