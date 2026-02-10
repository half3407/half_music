from fastapi import APIRouter, Depends, HTTPException
from db.db_server import DataBaseServer
from models.playlist import Playlist, PlaylistIn
from utils.token import get_current_user_id


session = DataBaseServer().get_session()
playlist_router = APIRouter(prefix="/playlists", tags=["歌单管理"])

#创建歌单（权限：普通用户和管理员），后续做权限验证
@playlist_router.post("/create")
def create_playlist(playlist: PlaylistIn,
                    #通过依赖注入获取当前用户ID
                    #用get_current_user_id函数解析token获取当前用户ID，确保只有登录用户才能创建歌单
                    current_user_id: int = Depends(get_current_user_id)
                    ):
    new_playlist = Playlist(
        playlist_name=playlist.playlist_name,
        playlist_creater=current_user_id
    )
    session.add(new_playlist)
    session.commit()
    session.refresh(new_playlist)
    return {"message": "歌单创建成功", 
            "playlist_id": new_playlist.id, 
            "playlist_name": new_playlist.playlist_name, 
            "playlist_creater": new_playlist.playlist_creater}

# 查看所有歌单（无权限要求）
@playlist_router.post("/view_all")
def get_all_playlists():
    playlists = session.query(Playlist).all()
    # 只返回歌单ID、名称和创建者，避免返回过多信息
    return {"playlists": [{"id": playlist.id, 
                           "name": playlist.playlist_name,
                             "creater_id": playlist.playlist_creater
                             } for playlist in playlists]}

# 查看某个歌单详情（无权限要求）
@playlist_router.post("/view_single/{playlist_id}")
def get_playlist(playlist_id: int):
    playlist = session.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    # 返回歌单所有信息
    return {"playlist": {"id": playlist.id, 
                         "name": playlist.playlist_name, 
                         "creater_id": playlist.playlist_creater,
                          "created_at": playlist.created_at, 
                          "updated_at": playlist.updated_at}}

#删除歌单（权限：歌单创建者或管理员，后续做权限验证）
@playlist_router.post("/delete/{playlist_id}")
def delete_playlist(playlist_id: int,
                    #通过依赖注入获取当前用户ID
                    #用get_current_user_id函数解析token获取当前用户ID，确保只有歌单创建者或管理员才能删除自己的歌单
                    current_user_id: int = Depends(get_current_user_id)):
    playlist = session.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    if str(playlist.playlist_creater) != str(current_user_id):
        raise HTTPException(status_code=403, detail="无权限删除该歌单")
    session.delete(playlist)
    session.commit()
    return {"message": "歌单删除成功"}

#修改歌单信息（权限：歌单创建者或管理员，后续做权限验证）
@playlist_router.post("/update/{playlist_id}")
def update_playlist(playlist_id: int, 
                    playlist: PlaylistIn,
                    #用get_current_user_id函数解析token获取当前用户ID，确保只有歌单创建者或管理员才能修改自己的歌单
                    current_user_id: int = Depends(get_current_user_id)):
    playlist_obj = session.query(Playlist).filter_by(id=playlist_id).first()
    if not playlist_obj:
        raise HTTPException(status_code=404, detail="歌单不存在")
    if str(playlist_obj.playlist_creater) != str(current_user_id):
        raise HTTPException(status_code=403, detail="无权限修改该歌单")
    #TODO 后续同步PlaylistIn增加更多字段的修改，比如歌单描述、封面等
    #TODO 之后写调用函数将除主键外的所有字段一键更新
    playlist_obj.playlist_name = playlist.playlist_name
    session.commit()
    return {"message": "歌单更新成功"}