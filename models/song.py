from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from models.base import MusicBase, SoftDeleteMixin, TimestampMixin


class Song(MusicBase, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    song_name: str = Column(String(255))
    song_singer: str = Column(String(255))
    song_lyricist: Optional[str] = Column(String(255), default="")
    song_composer: Optional[str] = Column(String(255), default="")
    song_album: Optional[str] = Column(String(255), default="")
    song_cover_url: Optional[str] = Column(String(255), default="")
    song_url: Optional[str] = Column(String(255), default="")
    creater_id: int = Column(Integer)

class SongIn(BaseModel):
    song_name: str
    song_singer: str
    song_lyricist: Optional[str] = ""
    song_composer: Optional[str] = ""
    song_album: Optional[str] = ""
    song_cover_url: Optional[str] = ""
    song_url: Optional[str] = ""


class SongOut(BaseModel):
    id: int
    song_name: str
    song_singer: str
    song_lyricist: Optional[str] = ""
    song_composer: Optional[str] = ""
    song_album: Optional[str] = ""
    song_cover_url: Optional[str] = ""
    song_url: Optional[str] = ""
    create_time: datetime
    update_time: datetime
    delete_time: Optional[datetime] = None