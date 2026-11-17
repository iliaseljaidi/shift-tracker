import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main import app
from database import Base, get_db

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)

def override_get_db():
    db_test = TestingSessionLocal()
    try:
        yield db_test
    finally:
        db_test.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)

def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def create_auth_header(client, email="a@example.com", password="password123"):
  client.post("/register", json={"email": email, "password": password})
  response = client.post("/login", data={"username": email, "password": password})
  token = response.json()["access_token"]
  return {"Authorization": f"Bearer {token}"}

SHIFT = {"venue": "Club X", "shift_date": "2026-10-10", "start_time": "22:00",
         "end_time": "04:00", "hourly_rate": 14.5}


def test_create_and_list_shift():
    headers = create_auth_header(client)
    response = client.post("/shifts", json=SHIFT, headers=headers)
    assert response.status_code == 201
    assert response.json()["hours"] == 6
    assert response.json()["pay"] == 87.0
    assert len(client.get("/shifts", headers=headers).json()) == 1

def test_users_cannot_see_each_others_shifts():
    a = create_auth_header(client, "a@example.com")
    b = create_auth_header(client, "b@example.com")

    shift_id = client.post("/shifts", json=SHIFT, headers=a).json()["id"]

    assert client.get("/shifts", headers=b).json() == []
    assert client.get(f"/shifts/{shift_id}", headers=b).status_code == 404