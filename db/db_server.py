from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import MusicBase

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

engine = create_engine("sqlite:///music.db?check_same_thread=False", echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    #显式初始化数据库（建表）
    MusicBase.metadata.create_all(engine)
