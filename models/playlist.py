from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from models.association import playlist_song_association
from models.base import MusicBase, SoftDeleteMixin, TimestampMixin




class Playlist(MusicBase,TimestampMixin, SoftDeleteMixin):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_name: str = Column(String(255))
    playlist_creater: str = Column(String(255))
    playlist_introduction: Optional[str] = Column(String(255), default="")
    playlist_cover_url: Optional[str] = Column(String(255), default="")
    playlist_cllect_num: int = Column(Integer, default=0)

    #定义与Song的多对多关系
    songs = relationship(
        "Song",
        secondary=playlist_song_association, 
        back_populates="playlists"
        )

    
class PlaylistIn(BaseModel):
    playlist_name: str
    playlist_introduction: Optional[str] = ""
    playlist_cover_url: Optional[str] = ""


class PlaylistOut(BaseModel):
    id: int
    playlist_name: str
    playlist_creater: str
    playlist_cllect_num: Optional[int] = 0
    playlist_introduction: Optional[str] = ""
    playlist_cover_url: Optional[str] = ""
    create_time: datetime
    update_time: datetime
    delete_time: Optional[datetime] = None