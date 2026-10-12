import argparse
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.db import Base
import app.models  # noqa: F401
from app.core.config import get_settings

TABLE_ORDER = [
    "institutes","users","platform_admins","departments","complaints",
    "complaint_workflow","complaint_history","announcements","notifications",
    "notification_preferences","campus_map_settings","campus_locations",
    "user_profiles","audit_logs","platform_settings"
]

def rows(conn, table):
    conn.row_factory = sqlite3.Row
    return [dict(r) for r in conn.execute(f'SELECT * FROM "{table}"').fetchall()]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", required=True, type=Path)
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.sqlite.exists():
        raise SystemExit(f"SQLite file not found: {args.sqlite}")
    settings = get_settings()
    url = args.database_url or settings.database_url
    source = sqlite3.connect(args.sqlite)
    counts = {t: len(rows(source,t)) for t in TABLE_ORDER}
    print("Source rows:")
    for t,c in counts.items(): print(f"  {t:28} {c}")
    if args.dry_run:
        print("Dry run: PostgreSQL was not changed.")
        return

    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        for table in reversed(TABLE_ORDER):
            db.execute(text(f'DELETE FROM "{table}"'))
        db.commit()

        for table in TABLE_ORDER:
            data = rows(source, table)
            if not data: continue
            columns = list(data[0].keys())
            cols = ", ".join(f'"{c}"' for c in columns)
            params = ", ".join(f':{c}' for c in columns)
            db.execute(text(f'INSERT INTO "{table}" ({cols}) VALUES ({params})'), data)
        db.commit()

        for table in TABLE_ORDER:
            if table == "platform_settings": continue
            try:
                max_id = db.execute(text(f'SELECT MAX(id) FROM "{table}"')).scalar()
                if max_id is not None:
                    db.execute(
                        text("SELECT setval(pg_get_serial_sequence(:table_name,'id'),:value,true)"),
                        {"table_name":table,"value":int(max_id)}
                    )
            except Exception:
                pass
        db.commit()
    source.close()
    print("Migration complete.")

if __name__ == "__main__":
    main()
