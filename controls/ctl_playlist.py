from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from db.db_server import DataBaseServer
from deps.database import get_db
from deps.pagination import PaginationParams, get_pagination
from deps.permissions import get_playlist_with_permission, require_authenticated, require_playlist_owner_or_admin
from models.playlist import Playlist, PlaylistIn
from sqlalchemy.orm import Session, joinedload
from models.user import User


playlist_router = APIRouter(prefix="/playlists", tags=["歌单管理"])

#创建歌单（权限：普通用户和管理员）
@playlist_router.post("/create")
def create_playlist(playlist: PlaylistIn,
                    user = Depends(require_authenticated),
                    db: Session = Depends(get_db)
                    ):
    new_playlist = Playlist(
        playlist_name=playlist.playlist_name,
        playlist_introduction=playlist.playlist_introduction,
        playlist_cover_url=playlist.playlist_cover_url,
        playlist_creater=user["user_id"]
    )
    db.add(new_playlist)
    db.commit()
    db.refresh(new_playlist)
    return {"message": "歌单创建成功", 
            "playlist_id": new_playlist.id, 
            "playlist_name": new_playlist.playlist_name, 
            "playlist_introduction": new_playlist.playlist_introduction,
            "playlist_cover_url": new_playlist.playlist_cover_url,
            "playlist_creater": new_playlist.playlist_creater}




# 查看所有歌单（无权限要求）
@playlist_router.post("/view_all")
def get_all_playlists(pagination: PaginationParams = Depends(get_pagination),
                      db: Session = Depends(get_db)):
    #分页查询，按照收藏数降序排序，每页显示12条数据
    playlists = db.query(Playlist).options(joinedload(Playlist.songs)).order_by(Playlist.playlist_cllect_num.desc()).offset((pagination.page-1)*pagination.page_size).limit(pagination.page_size).all()
    result = []
    for playlist in playlists:
        songs_data = [{
            "id": song.id,
            "name": song.song_name,
            "singer": song.song_singer,
            "cover_url": song.song_cover_url
        }
        for song in playlist.songs  #遍历关系对象
        ]
        result.append({
            "playlist": {
                "id": playlist.id,
                "name": playlist.playlist_name,
                "creater_id": playlist.playlist_creater,
                "created_at": playlist.created_at,
                "collect_num": playlist.playlist_cllect_num,
                "songs_count": len(songs_data)
            }
        })
    return result


#搜索歌单，无权限限制，模糊搜索歌单名
@playlist_router.post("/search_playlist")
def search_playlist(playlist_name: str,
                    pagination: PaginationParams = Depends(get_pagination),
                    db: Session = Depends(get_db)):
    #模糊搜索，分页查询，每页显示12条数据
    playlists = db.query(Playlist).options(joinedload(Playlist.songs)).filter(Playlist.playlist_name.like(f"%{playlist_name}%")).offset((pagination.page-1)*pagination.page_size).limit(pagination.page_size).all()
    result = []
    for playlist in playlists:
        songs_data = [{
            "id": song.id,
            "name": song.song_name,
            "singer": song.song_singer,
            "cover_url": song.song_cover_url
        }
        for song in playlist.songs  #遍历关系对象
        ]
        result.append({
            "playlist": {
                "id": playlist.id,
                "name": playlist.playlist_name,
                "creater_id": playlist.playlist_creater,
                "created_at": playlist.created_at,
                "collect_num": playlist.playlist_cllect_num,
                "songs_count": len(songs_data)
            }
        })
    return result

# 查看某个歌单详情（无权限要求）
@playlist_router.post("/view_single/{playlist_id}")
def get_playlist(playlist_id: int,
                 db: Session = Depends(get_db)):
    playlist = db.query(Playlist).options(joinedload(Playlist.songs)).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    songs_data = [{
            "id": song.id,
            "name": song.song_name,
            "singer": song.song_singer,
            "cover_url": song.song_cover_url
        }
        for song in playlist.songs  #遍历关系对象
    ]
    return {
        "playlist": {
            "id": playlist.id,
            "name": playlist.playlist_name,
            "creater_id": playlist.playlist_creater,
            "created_at": playlist.created_at,
            "updated_at": playlist.updated_at,
            "collect_num": playlist.playlist_cllect_num,
            "introduction": playlist.playlist_introduction,
            "cover_url": playlist.playlist_cover_url,
            "songs": songs_data,  #添加歌曲列表
            "songs_count": len(songs_data)
        }
    }

#收藏歌单（权限：普通用户）
@playlist_router.post("/collect/{playlist_id}")
def collect_playlist(playlist_id: int,
                     user = Depends(require_authenticated),
                     db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter_by(id=playlist_id).first()
    user = db.query(User).filter_by(id=user["user_id"]).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    #判断当前用户是否已收藏该歌单，如果已收藏则返回提示信息
    if str(playlist_id) in user.collected_playlists.split(","):
        raise HTTPException(status_code=400, detail="该用户已收藏该歌单")
    user.collected_playlists += f"{playlist_id},"
    playlist.playlist_cllect_num += 1
    db.commit()
    return {"message": "歌单收藏成功", "playlist_id": playlist.id, "current_collect_num": playlist.playlist_cllect_num}


#删除歌单（权限：歌单创建者或管理员）
@playlist_router.post("/delete/{playlist_id}")
def delete_playlist(playlist_id: int,
                    user = Depends(require_authenticated),
                    db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    db.delete(playlist)
    db.commit()
    return {"message": "歌单删除成功"}

#修改歌单信息（权限：歌单创建者或管理员）
@playlist_router.post("/update/{playlist_id}")
def update_playlist(playlist: PlaylistIn,
                    playlist_obj: Playlist = Depends(get_playlist_with_permission),
                    db: Session = Depends(get_db)):
    update_date = playlist.dict(exclude_unset=True)
    allowed_fields = ["playlist_name", "playlist_introduction", "playlist_cover_url"]
    update_fields = []
    for field, value in update_date.items():
        if field in allowed_fields:
            setattr(playlist_obj, field, value)
            update_fields.append(field)
    db.commit()
    return {
        "message": "歌单更新成功",
        "playlist_id": playlist_obj.id,
        "updated_fields": list(update_date.keys())
    }
