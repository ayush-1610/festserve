# create_users.py
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from festserve_api.database import SessionLocal
from festserve_api import models
from sqlalchemy.exc import ProgrammingError, OperationalError

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_users(db: Session = None):
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    # 1) remove any existing test data in the correct order
    from festserve_api import models
    try:
        db.query(models.ReportingSnapshot).delete()
        db.query(models.ScanEvent).delete()
        db.query(models.Campaign).delete()
        db.query(models.Advertiser).filter(models.Advertiser.contact_email == "adv@example.com").delete()
        db.query(models.ScannerUser).filter(models.ScannerUser.username == "scanner1").delete()
        db.commit()
    except (ProgrammingError, OperationalError):
        db.rollback()

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
    if close_db:
        db.close()

if __name__ == "__main__":
    create_users()
