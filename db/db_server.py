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


@singleton
class DataBaseServer:
    def __init__(self, db_path: str = "music.db"):
        self.engine = create_engine(f"sqlite:///{db_path}?check_same_thread=False", echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def init_db(self):
        #显式初始化数据库（建表）
        from models.base import MusicBase
        MusicBase.metadata.create_all(self.engine)

    def get_session(self):
        return self.session
