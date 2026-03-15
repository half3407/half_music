from fastapi import APIRouter, Depends, HTTPException, Query
from models.playlist import Playlist
from utils.token import get_current_user_info
from db.db_server import DataBaseServer
from models.song import Song, SongIn


session = DataBaseServer().get_session()
song_router = APIRouter(prefix="/songs", tags=["歌曲管理"])

#创建歌曲（权限：管理员）
@song_router.post("/create")
def create_song(song: SongIn,
                current_user_info: dict = Depends(get_current_user_info)):
    #显示当前用户角色以便调试
    print(f"当前用户角色: {current_user_info['role']}")
    if current_user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限创建歌曲")
    new_song = Song(
        song_name=song.song_name,
        song_singer=song.song_singer,
        song_lyricist=song.song_lyricist,
        song_composer=song.song_composer,
        song_album=song.song_album,
        song_cover_url=song.song_cover_url,
        song_url=song.song_url,
        creater_id=current_user_info["user_id"]
    )
    session.add(new_song)
    session.commit()
    return {"message": "歌曲创建成功", "song_id": new_song.id}

#删除歌曲（权限：管理员）
@song_router.post("/delete/{song_id}")
def delete_song(song_id: int, current_user_info: dict = Depends(get_current_user_info)):
    if current_user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限删除歌曲")
    song = session.query(Song).filter_by(id=song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    session.delete(song)
    session.commit()
    return {"message": "歌曲删除成功"}

#修改歌曲信息（权限：管理员）
@song_router.post("/update/{song_id}")
def update_song(song_id: int, 
                song: SongIn, 
                current_user_info: dict = Depends(get_current_user_info)
                ):
    if current_user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限修改歌曲信息")
    song_to_update = session.query(Song).filter_by(id=song_id).first()
    if not song_to_update:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    song_to_update.song_name = song.song_name
    song_to_update.song_singer = song.song_singer
    song_to_update.song_lyricist = song.song_lyricist
    song_to_update.song_composer = song.song_composer
    song_to_update.song_album = song.song_album
    song_to_update.song_cover_url = song.song_cover_url
    song_to_update.song_url = song.song_url
    session.commit()
    return {"message": "歌曲信息修改成功"}


#查看所有歌曲（无权限要求）
@song_router.post("/view_all")
def view_all_songs(page: int=Query(1,gt=0),page_size: int=Query(12,gt=0)):
    #按照创建时间排序，最新的歌曲在前面，分页查询，每页显示12条数据
    songs = session.query(Song).order_by(Song.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    result = []
    for song in songs:
        result.append({
            "id": song.id,
            "name": song.song_name,
            "singer": song.song_singer
        })
    return {"songs": result}


#搜索歌曲，无权限限制，模糊搜索歌曲名或歌手
@song_router.post("/search_song")
def search_song(keyword: str, page: int=Query(1,gt=0),page_size: int=Query(12,gt=0)):
    #模糊搜索，分页查询，每页显示12条数据
    songs = session.query(Song).filter((Song.song_name.like(f"%{keyword}%")) | (Song.song_singer.like(f"%{keyword}%"))).offset((page-1)*page_size).limit(page_size).all()
    result = []
    for song in songs:
        result.append({
            "id": song.id,
            "name": song.song_name,
            "singer": song.song_singer
        })
    return {"songs": result}



#查看某首歌曲详情（无权限要求）
#TODO:后续或可加入其他搜索条件如歌手、专辑等
@song_router.post("/view_single/{song_id}")
def view_single_song(song_id: int):
    song = session.query(Song).filter_by(id=song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    return {"song": {"id": song.id,
                     "name": song.song_name,
                     "singer": song.song_singer,
                     "lyricist": song.song_lyricist,
                     "composer": song.song_composer,
                     "album": song.song_album,
                     "cover_url": song.song_cover_url,
                     "url": song.song_url
                     }}


#添加歌曲到歌单（权限：歌单创建者或管理员）
@song_router.post("/add_to_playlist/{song_id}/{playlist_id}")
def add_song_to_playlist(song_id: int,
                        playlist_id: int, 
                        current_user_info: dict = Depends(get_current_user_info)
                        ):
    song = session.query(Song).filter_by(id=song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    playlist = session.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    if str(playlist.playlist_creater) != str(current_user_info["user_id"]) and current_user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限添加歌曲到该歌单")
    if song in playlist.songs:
        raise HTTPException(status_code=400, detail="该歌曲已在歌单中")
    playlist.songs.append(song)
    session.commit()
    return {"message": "歌曲添加到歌单成功", 
            "playlist_id": playlist.id, 
            "song_id": song.id,
            "current_songs_count": len(playlist.songs)}


#将歌曲从歌单中删除（权限：歌单创建者或管理员）
@song_router.post("/delete_from_playlist/{song_id}/{playlist_id}")
def delete_song_from_playlist(song_id: int,
                                playlist_id: int, 
                                current_user_info: dict = Depends(get_current_user_info)
                                ):
    song = session.query(Song).filter_by(id=song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    playlist = session.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    if str(playlist.playlist_creater) != str(current_user_info["user_id"]) and current_user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限移除该歌曲从该歌单")
    if song not in playlist.songs:
        raise HTTPException(status_code=400, detail="该歌曲不在歌单中")
    playlist.songs.remove(song)
    session.commit()
    return {"message": "歌曲从歌单移除成功", "playlist_id": playlist.id, "song_id": song.id}    
