def test_register_and_login(client):
    # Register new user
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user"]["username"] == "testuser"

    # Logout to clear session
    client.post("/api/auth/logout")

    # Login with registered credentials
    resp = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["user"]["username"] == "testuser"
