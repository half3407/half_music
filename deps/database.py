from db.db_server import DataBaseServer


def get_db():
    db = DataBaseServer().get_session()
    try:
        yield db
    finally:
        db.close()