from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from models.base import MusicBase, SoftDeleteMixin, TimestampMixin


class Playlist(MusicBase,TimestampMixin, SoftDeleteMixin):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_name: str = Column(String(255))
    playlist_creater: str = Column(String(255))

#TODO 这里歌单输入 信息需要补充更多字段，比如描述、封面等
class PlaylistIn(BaseModel):
    playlist_name: str


class PlaylistOut(BaseModel):
    id: int
    playlist_name: str
    playlist_creater: str
    create_time: datetime
    update_time: datetime
    delete_time: Optional[datetime] = None