from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, ForeignKey, Integer, String
from models.association import playlist_song_association
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
    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlists.id", name="fk_songs_playlist_id")
    )

    # 定义与Playlist的多对多关系
    playlists = relationship(
        "Playlist",
        back_populates="songs"
    )


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