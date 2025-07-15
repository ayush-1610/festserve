from datetime import datetime, date
from pydantic import BaseModel, UUID4

class CampaignCreate(BaseModel):
    stall_id: UUID4
    product_id: UUID4
    units_allocated: int
    start_datetime: datetime
    end_datetime: datetime

class CampaignRead(BaseModel):
    campaign_id: UUID4
    stall_id: UUID4
    product_id: UUID4
    units_allocated: int
    start_datetime: datetime
    end_datetime: datetime
    status: str

    class Config:
        orm_mode = True


class CampaignUpdate(BaseModel):
    units_allocated: int | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    status: str | None = None

    class Config:
        orm_mode = True


class ScanEventCreate(BaseModel):
    campaign_id: UUID4
    device_fingerprint: str | None = None

class ScanEventRead(BaseModel):
    scan_event_id: UUID4
    campaign_id: UUID4
    scanner_user_id: UUID4
    scanned_at: datetime
    device_fingerprint: str | None

    class Config:
        orm_mode = True


class StallCreate(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    date: date


class StallRead(StallCreate):
    stall_id: UUID4

    class Config:
        orm_mode = True


class ProductCreate(BaseModel):
    name: str
    description: str | None = None


class ProductRead(ProductCreate):
    product_id: UUID4

    class Config:
        orm_mode = True

class SnapshotRead(BaseModel):
    snapshot_id: UUID4
    campaign_id: UUID4
    snapshot_time: datetime
    total_scans: int
    remaining_units: int

    class Config:
        orm_mode = True
