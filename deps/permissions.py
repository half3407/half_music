from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from deps.database import get_db
from models.playlist import Playlist
from utils.token import get_current_user_info


def require_authenticated(user: dict = Depends(get_current_user_info)):
    if not user:
        raise HTTPException(status_code=401, detail="未认证")
    return user


def require_admin(user: dict = Depends(require_authenticated)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限")
    return user


def require_playlist_owner(playlist_id: int, 
                           user: dict = Depends(require_authenticated),
                           db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    #验证歌单是否存在
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="歌单不存在"
        )
    #验证歌单所有者
    if playlist.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="无权限操作该歌单")
    return user


def require_playlist_owner_or_admin(playlist_id: int, 
                                   user: dict = Depends(require_authenticated),
                                   db: Session = Depends(get_db)):
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    #验证歌单是否存在
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="歌单不存在"
        )
    #验证歌单所有者或管理员
    if playlist.user_id != user["user_id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限操作该歌单")
    return user


def require_user_self_or_admin(user_id: int, 
                          user: dict = Depends(require_authenticated)):
    if user["user_id"] != user_id and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限操作该用户")
    return user


def get_playlist_with_permission(playlist_id: int,
                                 user: dict = Depends(require_authenticated),
                                 db: Session = Depends(get_db)) -> Playlist:
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="歌单不存在")
    is_owner = str(playlist.playlist_creater) == str(user["user_id"])
    is_admin = user["role"] == "admin"
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="无权限查看该歌单")
    return playlist