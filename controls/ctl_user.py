from fastapi import APIRouter, Depends, HTTPException
from models.playlist import Playlist
from utils.token import generate_jwt_token, get_current_user_id
from db.db_server import DataBaseServer
from models.user import User, UserIn
import hashlib


session = DataBaseServer().get_session()
user_router = APIRouter(prefix="/users", tags=["用户管理"])


# 用户注册
@user_router.post("/register")
def register_user(user_in: UserIn):
    judg_user = session.query(User).filter_by(username=user_in.username).first()
    if judg_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user_in_hash = hashlib.md5()
    user_in_hash.update(user_in.password.encode('utf-8'))
    new_user = User(
        username=user_in.username,
        password_hash=user_in_hash.hexdigest()
    )
    session.add(new_user)
    session.commit()
    return {"message": "用户注册成功"}


# 用户登录
@user_router.post("/login")
def login_user(user_in: UserIn):
    judg_user = (
        session.query(User)
        .filter_by(
            username=user_in.username, 
            password_hash=hashlib.md5(user_in.password.encode('utf-8')).hexdigest()
            )
        .first()
    )
    if not judg_user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    session.commit()
    token_data = {
        "sub": str(judg_user.id), 
        "username": judg_user.username,
    }
    access_token = generate_jwt_token(judg_user.id)
    return {"access_token": access_token, "token_type": "bearer"}


#查看所有用户基本信息，用户名和用户ID（权限：管理员，后续做权限验证）
@user_router.post("/view_all_user")
def view_all_user():
    users = session.query(User).all()
    return {"users": [{"id": user.id, "username": user.username} for user in users]}


#查看某位用户详细信息（权限：用户本人或管理员，后续做权限验证）
@user_router.post("/view_single_user/{user_id}")
def view_single_user(user_id: int,
                     current_user_id: int = Depends(get_current_user_id)):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if str(user.id) != str(current_user_id):
        raise HTTPException(status_code=403, detail="无权限查看该用户信息")
    return {"user": user}


#修改用户信息（权限：用户本人或管理员，后续做权限验证）
@user_router.post("/update_user/{user_id}")
def update_user(user_id: int, 
                user_in: UserIn,
                current_user_id: int = Depends(get_current_user_id)):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if str(user.id) != str(current_user_id):
        raise HTTPException(status_code=403, detail="无权限修改该用户信息")
    #改用户名
    user.username = user_in.username
    #改密码
    user_in_hash = hashlib.md5()
    user_in_hash.update(user_in.password.encode('utf-8'))
    user.password_hash = user_in_hash.hexdigest()
    session.commit()
    return {"message": "用户信息更新成功"}

#注销用户（权限：用户本人或管理员，后续做权限验证）
#TODO：或可做自主选择是否将歌单一并删除，目前做法是删除用户时会删除该用户创建的所有歌单
@user_router.post("/delete_user/{user_id}")
def delete_user(user_id: int, 
                current_user_id: int = Depends(get_current_user_id)):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if str(user.id) != str(current_user_id):
        raise HTTPException(status_code=403, detail="无权限删除该用户")
    #验证通过后可再获取该用户的所有歌单并删除
    playlists = session.query(Playlist).filter_by(playlist_creater=user_id).all()
    for playlist in playlists:
        session.delete(playlist)
    session.delete(user)
    session.commit()
    return {"message": "用户删除成功"}
