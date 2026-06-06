import bcrypt
def hash_password(password: str) -> str:
    # bytes形式的哈希加密
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')   # 转为字符串方便存入数据库
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 密码校验
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )