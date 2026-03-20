from fastapi import APIRouter, Depends, HTTPException, Query
from db.db_server import DataBaseServer
from deps.database import get_db
from deps.pagination import PaginationParams, get_pagination
from models.playlist import Playlist, PlaylistIn
from sqlalchemy.orm import Session, joinedload
from models.user import User
from utils.token import get_current_user_info


playlist_router = APIRouter(prefix="/playlists", tags=["歌单管理"])

#创建歌单（权限：普通用户和管理员），后续做权限验证
@playlist_router.post("/create")
def create_playlist(playlist: PlaylistIn,
                    #通过依赖注入获取当前用户ID
                    #用get_current_user_info函数解析token获取当前用户ID，确保只有登录用户才能创建歌单
                    current_user_info: dict = Depends(get_current_user_info),
                    db: Session = Depends(get_db)
                    ):
    new_playlist = Playlist(
        playlist_name=playlist.playlist_name,
        playlist_introduction=playlist.playlist_introduction,
        playlist_cover_url=playlist.playlist_cover_url,
        playlist_creater=current_user_info["user_id"]
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
                     #通过依赖注入获取当前用户ID
                     #用get_current_user_info函数解析token获取当前用户ID，确保只有登录用户才能收藏歌单
                     current_user_info: dict = Depends(get_current_user_info),
                     db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter_by(id=playlist_id).first()
    user = db.query(User).filter_by(id=current_user_info["user_id"]).first()
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
                    #通过依赖注入获取当前用户ID
                    #用get_current_user_info函数解析token获取当前用户ID，确保只有歌单创建者或管理员才能删除自己的歌单
                    current_user_info: dict = Depends(get_current_user_info),
                    db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    if str(playlist.playlist_creater) != str(current_user_info["user_id"]) and current_user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限删除该歌单")
    db.delete(playlist)
    db.commit()
    return {"message": "歌单删除成功"}

#修改歌单信息（权限：歌单创建者或管理员）
@playlist_router.post("/update/{playlist_id}")
def update_playlist(playlist_id: int, 
                    playlist: PlaylistIn,
                    #用get_current_user_info函数解析token获取当前用户ID，确保只有歌单创建者或管理员才能修改自己的歌单
                    current_user_info: dict = Depends(get_current_user_info),
                    db: Session = Depends(get_db)):
    playlist_obj = db.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist_obj:
        raise HTTPException(status_code=404, detail="歌单不存在")
    if str(playlist_obj.playlist_creater) != str(current_user_info["user_id"]) and current_user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限修改该歌单")
    #TODO 之后写调用函数将除主键外的所有字段一键更新
    playlist_obj.playlist_name = playlist.playlist_name
    playlist_obj.playlist_introduction = playlist.playlist_introduction
    playlist_obj.playlist_cover_url = playlist.playlist_cover_url
    db.commit()
    return {"message": "歌单更新成功"}
