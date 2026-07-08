def login(client, username: str = "admin", password: str = "admin12345") -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_full_lead_lifecycle(client) -> None:
    headers = login(client)

    statuses = client.get("/api/v1/dictionaries/statuses", headers=headers).json()
    courses = client.get("/api/v1/dictionaries/courses", headers=headers).json()
    sources = client.get("/api/v1/dictionaries/sources", headers=headers).json()
    users = client.get("/api/v1/users", headers=headers).json()

    assert len(statuses) >= 3
    assert len(courses) == 1
    assert len(sources) == 1
    assert {user["username"] for user in users} == {"admin", "manager"}

    manager = next(user for user in users if user["username"] == "manager")
    create_response = client.post(
        "/api/v1/leads",
        headers=headers,
        json={
            "customer_name": "Иван Петров",
            "contact": "+79990000000",
            "notes": "Первичная тестовая заявка",
            "status_id": statuses[0]["id"],
            "course_id": courses[0]["id"],
            "source_id": sources[0]["id"],
            "assigned_manager_id": manager["id"],
            "next_contact_date": "2026-07-07",
        },
    )
    assert create_response.status_code == 201
    lead = create_response.json()
    assert lead["customer_name"] == "Иван Петров"
    assert lead["assigned_manager"]["username"] == "manager"
    assert lead["next_contact_date"] == "2026-07-07"
    assert len(lead["comments"]) == 1

    filtered = client.get(
        "/api/v1/leads",
        headers=headers,
        params={
            "status_id": statuses[0]["id"],
            "course_id": courses[0]["id"],
            "source_id": sources[0]["id"],
            "assigned_manager_id": manager["id"],
            "search": "Петров",
        },
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    overdue = client.get("/api/v1/leads", headers=headers, params={"overdue": True})
    assert overdue.status_code == 200
    assert overdue.json()["total"] == 1

    export_response = client.get("/api/v1/leads/export.csv", headers=headers)
    assert export_response.status_code == 200
    assert "text/csv" in export_response.headers["content-type"]
    assert "customer_name" in export_response.text
    assert "Иван Петров" in export_response.text

    summary_response = client.get("/api/v1/reports/summary", headers=headers)
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["kpi"]["total"] == 1
    assert summary["kpi"]["overdue"] == 1

    update_response = client.patch(
        f"/api/v1/leads/{lead['id']}",
        headers=headers,
        json={"status_id": statuses[1]["id"], "notes": "Статус изменен"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["status_id"] == statuses[1]["id"]
    assert updated["notes"] == "Статус изменен"

    comment_response = client.post(
        f"/api/v1/leads/{lead['id']}/comments",
        headers=headers,
        json={"body": "Клиенту отправлена программа курса"},
    )
    assert comment_response.status_code == 201
    assert comment_response.json()["body"] == "Клиенту отправлена программа курса"

    comments = client.get(f"/api/v1/leads/{lead['id']}/comments", headers=headers)
    assert comments.status_code == 200
    assert len(comments.json()) == 3

    delete_response = client.delete(f"/api/v1/leads/{lead['id']}", headers=headers)
    assert delete_response.status_code == 200

    list_after_delete = client.get("/api/v1/leads", headers=headers)
    assert list_after_delete.status_code == 200
    assert list_after_delete.json()["total"] == 0


def test_lead_reference_validation(client) -> None:
    headers = login(client)

    response = client.post(
        "/api/v1/leads",
        headers=headers,
        json={
            "customer_name": "Некорректная заявка",
            "contact": "test",
            "status_id": 999999,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["status_id"] == "Status does not exist or is inactive"


def test_manager_cannot_create_users(client) -> None:
    headers = login(client, "manager", "manager12345")

    response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "username": "new-manager",
            "password": "manager12345",
            "full_name": "New Manager",
            "role": "manager",
        },
    )

    assert response.status_code == 403


def test_manager_sees_only_assigned_leads(client) -> None:
    admin_headers = login(client)
    manager_headers = login(client, "manager", "manager12345")

    statuses = client.get("/api/v1/dictionaries/statuses", headers=admin_headers).json()
    users = client.get("/api/v1/users", headers=admin_headers).json()
    manager = next(user for user in users if user["username"] == "manager")

    own_response = client.post(
        "/api/v1/leads",
        headers=admin_headers,
        json={
            "customer_name": "Своя заявка",
            "contact": "+79991111111",
            "status_id": statuses[0]["id"],
            "assigned_manager_id": manager["id"],
        },
    )
    foreign_response = client.post(
        "/api/v1/leads",
        headers=admin_headers,
        json={
            "customer_name": "Чужая заявка",
            "contact": "+79992222222",
            "status_id": statuses[0]["id"],
        },
    )
    assert own_response.status_code == 201
    assert foreign_response.status_code == 201

    manager_list = client.get("/api/v1/leads", headers=manager_headers)
    assert manager_list.status_code == 200
    assert manager_list.json()["total"] == 1
    assert manager_list.json()["items"][0]["customer_name"] == "Своя заявка"

    foreign_id = foreign_response.json()["id"]
    forbidden = client.get(f"/api/v1/leads/{foreign_id}", headers=manager_headers)
    assert forbidden.status_code == 404

    manager_create = client.post(
        "/api/v1/leads",
        headers=manager_headers,
        json={
            "customer_name": "Создана менеджером",
            "contact": "+79993333333",
            "status_id": statuses[0]["id"],
        },
    )
    assert manager_create.status_code == 201
    assert manager_create.json()["assigned_manager"]["username"] == "manager"
