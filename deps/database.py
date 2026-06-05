from db.db_server import SessionLocal


def get_db():
    # 通过sessionmaker创建一个新的数据库会话，并在请求结束后关闭它
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()