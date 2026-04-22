from fastapi import APIRouter, Depends, HTTPException, Query
from deps.pagination import PaginationParams, get_pagination
from sqlalchemy.orm import Session
from deps.database import get_db
from models.playlist import Playlist
from utils.token import generate_jwt_token
from deps.permissions import require_user_self_or_admin
from db.db_server import DataBaseServer
from models.user import User, UserIn
import hashlib


user_router = APIRouter(prefix="/users", tags=["用户管理"])


# 用户注册
@user_router.post("/register")
def register_user(user_in: UserIn,
                  db: Session = Depends(get_db)):
    judg_user = db.query(User).filter_by(username=user_in.username).first()
    if judg_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user_in_hash = hashlib.md5()
    user_in_hash.update(user_in.password.encode('utf-8'))
    new_user = User(
        username=user_in.username,
        password_hash=user_in_hash.hexdigest(),
        role=user_in.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "用户注册成功"}


# 用户登录
@user_router.post("/login")
def login_user(user_in: UserIn, db: Session = Depends(get_db)):
    judg_user = (
        db.query(User)
        .filter_by(
            username=user_in.username, 
            password_hash=hashlib.md5(user_in.password.encode('utf-8')).hexdigest()
            )
        .first()
    )
    if not judg_user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    db.commit()
    token_data = {
        "sub": str(judg_user.id), 
        "username": judg_user.username,
        "role": judg_user.role
    }
    access_token = generate_jwt_token(judg_user.id, judg_user.role)
    return {"access_token": access_token,
             "token_type": "bearer",
             "user_id": judg_user.id,
             "username": judg_user.username,
             "role": judg_user.role}


#查看所有用户基本信息，用户名和用户ID
@user_router.post("/view_all_user")
def view_all_user(page: int=Query(1,gt=0),
                  page_size: int=Query(12,gt=0),
                  db: Session = Depends(get_db)):
    #分页查询，每页显示12条数据
    #TODO：后续完成用户关注功能这里可以按照被关注数排序
    users = db.query(User).offset((page-1)*page_size).limit(page_size).all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "role": user.role
        })
    return {"users": result}


#搜索用户，无权限限制，模糊搜索用户名
@user_router.post("/search_user")
def search_user(username: str,
                pagination: PaginationParams = Depends(get_pagination),
                db: Session = Depends(get_db)):
    #模糊搜索，分页查询，每页显示12条数据
    users = db.query(User).filter(User.username.like(f"%{username}%")).offset((pagination.page-1)*pagination.page_size).limit(pagination.page_size).all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username
        })
    return {"users": result}

#查看某位用户详细信息（权限：用户本人或管理员）
@user_router.post("/view_single_user/{user_id}")
def view_single_user(user_id: int,
                     user: dict = Depends(require_user_self_or_admin),
                     db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"user": user}


#修改用户信息（权限：用户本人或管理员）
@user_router.post("/update_user/{user_id}")
def update_user(user_id: int, 
                user_in: UserIn,
                user: dict = Depends(require_user_self_or_admin),
                db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    #改用户名
    user.username = user_in.username
    #改密码
    user_in_hash = hashlib.md5()
    user_in_hash.update(user_in.password.encode('utf-8'))
    user.password_hash = user_in_hash.hexdigest()
    db.commit()
    return {"message": "用户信息更新成功"}

#注销用户（权限：用户本人或管理员）
@user_router.post("/delete_user/{user_id}")
def delete_user(
    user_id: int,
    delete_playlists: bool = True,
    user: dict = Depends(require_user_self_or_admin),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter_by(id=user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    playlists_query = db.query(Playlist).filter_by(playlist_creater=user_id)
    
    if delete_playlists:
        # 删除该用户创建的所有歌单
        playlists = playlists_query.all()
        for playlist in playlists:
            db.delete(playlist)
        operation_msg = "并已删除其创建的所有歌单"
    else:
        # 保留歌单，将creater标记为0
        updated_count = playlists_query.update(
            {"playlist_creater": 0}, 
            synchronize_session=False  # 提升批量更新效率
        )
        operation_msg = f"并保留{updated_count}个歌单（creater标记为0）"
    
    db.delete(target_user)
    db.commit()
    
    return {
        "message": f"用户删除成功{operation_msg}",
        "playlists_handled": "deleted" if delete_playlists else "transferred_to_system"
    }