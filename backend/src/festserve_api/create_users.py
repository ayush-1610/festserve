# create_users.py
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from festserve_api.database import SessionLocal
from festserve_api import models

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_users():
    db: Session = SessionLocal()

    # 1) remove any existing test data in the correct order
    from festserve_api import models
    db.query(models.ReportingSnapshot).delete()
    db.query(models.ScanEvent).delete()
    db.query(models.Campaign).delete()
    db.query(models.Advertiser).filter(models.Advertiser.contact_email == "adv@example.com").delete()
    db.query(models.ScannerUser).filter(models.ScannerUser.username == "scanner1").delete()
    db.commit()

    # 2) now re-insert
    adv = models.Advertiser(
        name="Test Advertiser",
        contact_email="adv@example.com",
        password_hash=pwd_ctx.hash("advpassword123"),
    )
    scanner = models.ScannerUser(
        username="scanner1",
        password_hash=pwd_ctx.hash("scanpassword123"),
        assigned_stall_id=None,
    )
    db.add_all([adv, scanner])
    db.commit()
    print("Created test users")
    db.close()

if __name__ == "__main__":
    create_users()
