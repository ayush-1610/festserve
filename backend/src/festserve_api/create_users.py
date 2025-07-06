# create_users.py
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from festserve_api.database import SessionLocal
from festserve_api import models

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_users():
    db: Session = SessionLocal()
    # Advertiser
    adv = models.Advertiser(
        name="Test Advertiser",
        contact_email="adv@example.com",
        password_hash=pwd_ctx.hash("advpassword123")
    )
    # Scanner
    scanner = models.ScannerUser(
        username="scanner1",
        password_hash=pwd_ctx.hash("scanpassword123"),
        assigned_stall_id=None  # assign later or set a valid stall UUID
    )
    db.add_all([adv, scanner])
    db.commit()
    print("Created test users")
    db.close()

if __name__ == "__main__":
    create_users()
