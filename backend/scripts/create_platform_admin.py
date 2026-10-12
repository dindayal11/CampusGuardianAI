import argparse
from getpass import getpass
from app.core.security import hash_password
from app.db import SessionLocal
from app.models import PlatformAdmin
from app.services.audit import now_text

def main():
    parser=argparse.ArgumentParser(description="Create the first Campus Guardian AI Platform Admin.")
    parser.add_argument("--admin-id",required=True)
    parser.add_argument("--name",required=True)
    parser.add_argument("--email",required=True)
    args=parser.parse_args()
    password=getpass("Password (minimum 12 characters): ")
    if len(password)<12:
        raise SystemExit("Use a password of at least 12 characters.")
    db=SessionLocal()
    try:
        if db.query(PlatformAdmin).filter(PlatformAdmin.email==args.email.lower()).first():
            raise SystemExit("A Platform Admin with this email already exists.")
        db.add(PlatformAdmin(admin_id=args.admin_id.strip(),name=args.name.strip(),email=args.email.lower().strip(),
                             password=hash_password(password),status="Active",created_at=now_text()))
        db.commit()
        print("Platform Admin created successfully.")
    finally:
        db.close()
if __name__=="__main__":
    main()
