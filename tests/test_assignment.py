
def register_user(client):
    return client.post(
        "/api/auth/register",
        json={
            "username": "assignuser",
            "email": "assign@example.com",
            "password": "password123",
            "first_name": "Assign",
            "last_name": "User",
        },
    )


def create_student(client):
    return client.post(
        "/api/students",
        json={
            "first_name": "Johnny",
            "last_name": "Doe",
            "date_of_birth": "2010-01-01",
            "grade_level": "5",
        },
    )


def test_create_assignment_flow(client):
    # Register and logged in user
    resp = register_user(client)
    assert resp.status_code == 201

    # Create a student
    s_resp = create_student(client)
    assert s_resp.status_code == 201
    student_id = s_resp.get_json()["student"]["id"]

    # Create an assignment for the student
    a_resp = client.post(
        "/api/assignments",
        json={"student_id": student_id, "title": "Math homework"},
    )
    assert a_resp.status_code == 201
    assignment = a_resp.get_json()["assignment"]
    assert assignment["title"] == "Math homework"

    # List assignments and ensure the new one is returned
    list_resp = client.get("/api/assignments")
    assert list_resp.status_code == 200
    assignments = list_resp.get_json()
    assert any(a["id"] == assignment["id"] for a in assignments)
