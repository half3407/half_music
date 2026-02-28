from fastapi import APIRouter, Depends, HTTPException
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
def update_song(song_id: int, song: SongIn, current_user_info: dict = Depends(get_current_user_info)):
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
def view_all_songs():
    songs = session.query(Song).all()
    return {"songs": [{"id": song.id,
                        "name": song.song_name,
                        "singer": song.song_singer,
                        "cover_url": song.song_cover_url,
                        "url": song.song_url
                        } for song in songs]}

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