from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import MusicBase

engine = create_engine("sqlite:///music.db?check_same_thread=False", echo=True)
# 使用sessionmaker创建一个数据库会话工厂，并绑定到engine以供调用生产数据库会话
SessionLocal = sessionmaker(bind=engine)

def init_db():
    #显式初始化数据库（建表）
    MusicBase.metadata.create_all(engine)
