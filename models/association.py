from sqlalchemy import Table, Column, Integer, ForeignKey
from models.base import MusicBase






playlist_song_association = Table(
    'playlist_song_association',
    MusicBase.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
    Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True)
)