'''
SQLAlchemy models and Alembic setup for festserve backend
'''
from datetime import datetime
import enum
import uuid

from sqlalchemy import (
    Column, String, Integer, Date, DateTime, Float, Enum, ForeignKey, text, UniqueConstraint
)
from passlib.context import CryptContext

from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text


# Base = declarative_base()

# import the shared Base from database.py instead:
from festserve_api.database import Base

# ENUM for campaign status
class CampaignStatus(str, enum.Enum):
    scheduled = 'scheduled'
    active = 'active'
    completed = 'completed'

class Advertiser(Base):
    __tablename__ = 'advertisers'
    advertiser_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)     # ← new

    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    campaigns = relationship('Campaign', back_populates='advertiser')

class Stall(Base):
    __tablename__ = 'stalls'
    stall_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    campaigns = relationship('Campaign', back_populates='stall')
    __table_args__ = (
        UniqueConstraint('location_name', 'date', name='uq_stall_location_date'),
    )

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)

    campaigns = relationship('Campaign', back_populates='product')

class ScannerUser(Base):
    __tablename__ = 'scanner_users'
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    assigned_stall_id = Column(UUID(as_uuid=True), ForeignKey('stalls.stall_id'), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))

    stall = relationship('Stall')
    scan_events = relationship('ScanEvent', back_populates='scanner')

class Campaign(Base):
    __tablename__ = 'campaigns'
    campaign_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    advertiser_id = Column(UUID(as_uuid=True), ForeignKey('advertisers.advertiser_id'), nullable=False)
    stall_id = Column(UUID(as_uuid=True), ForeignKey('stalls.stall_id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
    units_allocated = Column(Integer, nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    status = Column(Enum(CampaignStatus), nullable=False, default=CampaignStatus.scheduled)

    advertiser = relationship('Advertiser', back_populates='campaigns')
    stall = relationship('Stall', back_populates='campaigns')
    product = relationship('Product', back_populates='campaigns')
    scan_events = relationship('ScanEvent', back_populates='campaign')
    snapshots = relationship('ReportingSnapshot', back_populates='campaign')

    __table_args__ = (
        UniqueConstraint('advertiser_id', 'stall_id', 'product_id', 'start_datetime', name='uq_campaign_unique_run'),
    )

class ScanEvent(Base):
    __tablename__ = 'scan_events'
    scan_event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.campaign_id'), nullable=False)
    scanner_user_id = Column(UUID(as_uuid=True), ForeignKey('scanner_users.user_id'), nullable=False)
    scanned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    device_fingerprint = Column(String)

    campaign = relationship('Campaign', back_populates='scan_events')
    scanner = relationship('ScannerUser', back_populates='scan_events')

    __table_args__ = (
        # index for fast time-based filtering
        {'sqlite_autoincrement': True},
    )

class ReportingSnapshot(Base):
    __tablename__ = 'reporting_snapshots'
    snapshot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.campaign_id'), nullable=False)
    snapshot_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_scans = Column(Integer, nullable=False)
    remaining_units = Column(Integer, nullable=False)

    campaign = relationship('Campaign', back_populates='snapshots')

# Alembic env.py snippet to include metadata
# in alembic/env.py:
# from backend.src.festserve_api.models import Base
# target_metadata = Base.metadata

# Initial migration (CLI)
# alembic revision --autogenerate -m "create core tables"
# alembic upgrade head
