import sys
import os

print("🔧 conftest 加载中...")
print(f"🔧 当前目录: {os.getcwd()}")
print(f"🔧 sys.path: {sys.path}")



sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 关键：在导入 main 之前，先替换数据库配置
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Monkey-patch DataBaseServer，让它用我们的测试引擎
import db.db_server as db_server_module
original_init = db_server_module.DataBaseServer.__init__

def patched_init(self, db_path="music.db"):
    self.engine = test_engine
    from models.base import MusicBase
    Session = sessionmaker(bind=self.engine)
    self.session = Session()

db_server_module.DataBaseServer.__init__ = patched_init

# 现在导入 main
from main import app
from models.base import MusicBase
from deps.database import get_db

import pytest
from fastapi.testclient import TestClient

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    # 确保表已创建
    MusicBase.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    # 清理
    MusicBase.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token(client):
    client.post("/api/v1/users/register", json={
        "username": "admin",
        "password": "admin123",
        "role": "admin"
    })
    resp = client.post("/api/v1/users/login", json={
        "username": "admin",
        "password": "admin123"
    })
    return resp.json()["access_token"]

@pytest.fixture
def user_token(client):
    client.post("/api/v1/users/register", json={
        "username": "user1",
        "password": "user123",
        "role": "user"
    })
    resp = client.post("/api/v1/users/login", json={
        "username": "user1",
        "password": "user123"
    })
    return resp.json()["access_token"]