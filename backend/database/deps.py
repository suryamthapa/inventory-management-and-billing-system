from backend.database.setup import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()