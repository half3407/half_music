import os
import time

from fastapi import HTTPException, Header
import jwt  

JWT_TOKEN_EXPIRE_TIME = os.environ.get('JWT_TOKEN_EXPIRE_TIME', 3600 * 2)  # token有效时间 2小时
JWT_SECRET:str = os.environ.get('JWT_SECRET', '7m#L9v@Qx2pKf$Rn8sW4eY6!zA1hC5tG')   # 加解密密钥
JWT_ALGORITHM:str = os.environ.get('JWT_ALGORITHM', 'HS256')  # 加解密算法

# 生成token
def generate_jwt_token(user_id: int, role: str)->str:
    payload = {'user_id': user_id, 'role': role, 'exp': int(time.time()) + JWT_TOKEN_EXPIRE_TIME}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


# 获取当前用户ID和role的依赖函数
#TODO：后续应从路由层面进行权限控制，无权限则直接无法访问路由
def get_current_user_info(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token格式错误")
    token = authorization[7:].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        exp = payload.get("exp")
        if user_id is None or exp is None:
            raise HTTPException(status_code=401, detail="Token无效")
        if time.time() > exp:
            raise HTTPException(status_code=401, detail="Token已过期")
        return {"user_id": user_id, "role": role}
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Token解析失败")