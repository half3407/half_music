from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from deps.database import get_db
from deps.pagination import PaginationParams, get_pagination
from deps.permissions import require_admin, require_playlist_owner, require_playlist_owner_or_admin
from models.playlist import Playlist
from models.song import Song, SongIn
from utils.redis_client import get_cache, set_cache, delete_pattern
from utils.redis_client import r  # 导入 Redis 连接对象


song_router = APIRouter(prefix="/songs", tags=["歌曲管理"])

#创建歌曲（权限：管理员）
@song_router.post("/create")
def create_song(song: SongIn,
                user: dict = Depends(require_admin),
                db: Session = Depends(get_db)):
    new_song = Song(
        song_name=song.song_name,
        song_singer=song.song_singer,
        song_lyricist=song.song_lyricist,
        song_composer=song.song_composer,
        song_album=song.song_album,
        song_cover_url=song.song_cover_url,
        song_url=song.song_url,
        creater_id=user["user_id"]
    )
    db.add(new_song)
    db.commit()
    delete_pattern("song:page:*")
    return {"message": "歌曲创建成功", "song_id": new_song.id}

#删除歌曲（权限：管理员）
@song_router.post("/delete/{song_id}")
def delete_song(song_id: int,
                user: dict = Depends(require_admin),
                db: Session = Depends(get_db)):
    song = db.query(Song).filter_by(id=song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    db.delete(song)
    db.commit()
    delete_pattern("song:page:*")
    delete_pattern("playlists:page:*")
    r.delete(f"playlist:{song_id}") # 只删除当前歌单的缓存
    return {"message": "歌曲删除成功"}

#修改歌曲信息（权限：管理员）
@song_router.post("/update/{song_id}")
def update_song(song_id: int, 
                song: SongIn, 
                user: dict = Depends(require_admin),
                db: Session = Depends(get_db)
                ):
    song_to_update = db.query(Song).filter_by(id=song_id).first()
    if not song_to_update:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    song_to_update.song_name = song.song_name
    song_to_update.song_singer = song.song_singer
    song_to_update.song_lyricist = song.song_lyricist
    song_to_update.song_composer = song.song_composer
    song_to_update.song_album = song.song_album
    song_to_update.song_cover_url = song.song_cover_url
    song_to_update.song_url = song.song_url
    db.commit()
    delete_pattern("playlists:page:*")
    delete_pattern("song:page:*")
    r.delete(f"playlist:{song_to_update.id}") # 只删除当前歌单的缓存
    delete_pattern(f"playlist:{song_to_update.id}")
    return {"message": "歌曲信息修改成功"}


#查看所有歌曲（无权限要求）
@song_router.post("/view_all")
def view_all_songs(pagination: PaginationParams = Depends(get_pagination),
                    db: Session = Depends(get_db)):
    cache_key = f"songs:page:{pagination.page}"
    cached_date = get_cache(cache_key)
    if cached_date:
        return cached_date
    #按照创建时间排序，最新的歌曲在前面，分页查询，每页显示12条数据
    songs = db.query(Song)\
              .order_by(Song.created_at.desc())\
              .offset((pagination.page-1)*pagination.page_size)\
              .limit(pagination.page_size).all()
    result = []
    for song in songs:
        result.append({
            "id": song.id,
            "name": song.song_name,
            "singer": song.song_singer,
            "url": song.song_url,
            "cover_url": song.song_cover_url
        })
    set_cache(cache_key, result, expire=300)
    return {"songs": result}


#搜索歌曲，无权限限制，模糊搜索歌曲名或歌手
@song_router.post("/search_song")
def search_song(keyword: str,
                pagination: PaginationParams = Depends(get_pagination),
                db: Session = Depends(get_db)):
    #模糊搜索，分页查询，每页显示12条数据
    songs = db.query(Song).filter((Song.song_name.like(f"%{keyword}%")) | (Song.song_singer.like(f"%{keyword}%"))).offset((pagination.page-1)*pagination.page_size).limit(pagination.page_size).all()
    result = []
    for song in songs:
        result.append({
            "id": song.id,
            "name": song.song_name,
            "singer": song.song_singer,
            "url": song.song_url,
            "cover_url": song.song_cover_url
        })
    return {"songs": result}



#查看某首歌曲详情（无权限要求）
@song_router.post("/view_single/{song_id}")
def view_single_song(song_id: int,
                     db: Session = Depends(get_db)):
    song = db.query(Song).filter_by(id=song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    result = {"song": {"id": song.id,
                     "name": song.song_name,
                     "singer": song.song_singer,
                     "lyricist": song.song_lyricist,
                     "composer": song.song_composer,
                     "album": song.song_album,
                     "cover_url": song.song_cover_url,
                     "url": song.song_url
                     }}
    return result


#添加歌曲到歌单（权限：歌单创建者）
@song_router.post("/add_to_playlist/{song_id}/{playlist_id}")
def add_song_to_playlist(song_id: int,
                         playlist_id: int, 
                         user: dict = Depends(require_playlist_owner),
                         db: Session = Depends(get_db)
                        ):
    song = db.query(Song).filter_by(id=song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    playlist = db.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    if song in playlist.songs:
        raise HTTPException(status_code=400, detail="该歌曲已在歌单中")
    playlist.songs.append(song)
    db.commit()
    # 因为歌曲信息改变了，可能会影响歌单详情页的缓存，所以删除相关缓存
    delete_pattern("playlists:page:*")
    r.delete(f"playlist:{playlist.id}") # 只删除当前歌单的缓存
    delete_pattern(f"playlist:{playlist.id}")
    return {"message": "歌曲添加到歌单成功", 
            "playlist_id": playlist.id, 
            "song_id": song.id,
            "current_songs_count": len(playlist.songs)}


#将歌曲从歌单中删除（权限：歌单创建者）
@song_router.post("/delete_from_playlist/{song_id}/{playlist_id}")
def delete_song_from_playlist(song_id: int,
                              playlist_id: int,
                              user: dict = Depends(require_playlist_owner),
                              db: Session = Depends(get_db)
                                ):
    song = db.query(Song).filter_by(id=song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    playlist = db.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    if song not in playlist.songs:
        raise HTTPException(status_code=400, detail="该歌曲不在歌单中")
    playlist.songs.remove(song)
    db.commit()
    # 因为歌曲信息改变了，可能会影响歌单详情页的缓存，所以删除相关缓存
    delete_pattern("playlists:page:*")
    r.delete(f"playlist:{playlist.id}") # 只删除当前歌单的缓存
    delete_pattern(f"playlist:{playlist_id}")
    return {"message": "歌曲从歌单移除成功", "playlist_id": playlist.id, "song_id": song.id}    
