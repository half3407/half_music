import bcrypt

# 这个文件封装了"密码加密"和"密码校验"两个功能。
# 全项目凡是涉及密码的地方，都只调用这里的函数，不直接碰加密细节。


def hash_password(password: str) -> str:
    # 用 utf-8 把字符串编码成 bytes
    password_bytes = password.encode("utf-8")
    # 加盐
    salt = bcrypt.gensalt()
    # 把密码和盐一起哈希
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # 把 bytes 解码回 str 再返回
    return hashed_bytes.decode("utf-8")
# 验证密码是否正确：把用户输入的密码和数据库里存的哈希一起用 bcrypt 的校验函数验证
def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"), 
        )
    except ValueError:
        return False
