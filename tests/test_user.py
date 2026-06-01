def test_register_success(client):
    response = client.post("/api/v1/users/register", json={
        "username": "testuser",
        "password": "testpass",
        "role": "user"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "用户注册成功"

def test_register_duplicate_username(client):
    # 第一次注册
    client.post("/api/v1/users/register", json={
        "username": "testuser",
        "password": "testpass",
        "role": "user"
    })
    # 重复注册
    response = client.post("/api/v1/users/register", json={
        "username": "testuser",
        "password": "testpass",
        "role": "user"
    })
    assert response.status_code == 400
    assert "用户名已存在" in response.json()["detail"]

def test_login_success(client):
    # 先注册
    client.post("/api/v1/users/register", json={
        "username": "testuser",
        "password": "testpass",
        "role": "user"
    })
    # 登录
    response = client.post("/api/v1/users/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    # 先注册
    client.post("/api/v1/users/register", json={
        "username": "testuser",
        "password": "testpass",
        "role": "user"
    })
    # 错误密码
    response = client.post("/api/v1/users/login", json={
        "username": "testuser",
        "password": "wrongpass"
    })
    assert response.status_code == 401

def test_get_user_info_with_auth(client, user_token):
    response = client.post(
        "/api/v1/users/view_single_user/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert "user" in response.json()

def test_get_user_info_without_auth(client):
    response = client.post("/api/v1/users/view_single_user/1")
    assert response.status_code == 401