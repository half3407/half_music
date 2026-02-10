from fastapi import APIRouter, HTTPException
from db.db_server import DataBaseServer
from models.user import User, UserIn
import hashlib

from utils.token import generate_jwt_token

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

#查看用户信息（权限：用户本人或管理员，后续做权限验证）





#修改用户信息（权限：用户本人或管理员，后续做权限验证）