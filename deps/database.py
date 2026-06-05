from db.db_server import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()