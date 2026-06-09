import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import MusicBase

engine = create_engine("sqlite:///music.db?check_same_thread=False", echo=True)
# 使用sessionmaker创建一个数据库会话工厂，并绑定到engine以供调用生产数据库会话
SessionLocal = sessionmaker(bind=engine)

def init_db():
    #显式初始化数据库（建表）
    MusicBase.metadata.create_all(engine)

# 初始化数据库时顺便创建一个初始管理员账号，方便第一次启动后就能登录后台设置其他管理员
def init_first_admin():
    from models.user import User
    from utils.security import hash_password

    username = os.environ.get("INIT_ADMIN_USERNAME")
    password = os.environ.get("INIT_ADMIN_PASSWORD")
    # 如果没有配置就跳过，需要去数据库改role=admin
    if not username or not password:
        return

    db = SessionLocal()
    try:
        # 只要库里已经存在管理员，就不创建了，避免重复创建多个管理员账号。
        existing_admin = db.query(User).filter_by(role="admin").first()
        if existing_admin:
            return

        # 库里还没有管理员，才创建。密码同样用 bcrypt 加密后存储。
        admin = User(
            username=username,
            password_hash=hash_password(password),
            role="admin",
        )
        db.add(admin)
        db.commit()
        print(f"[INIT] 已创建初始管理员账号: {username}")
    finally:
        db.close()
