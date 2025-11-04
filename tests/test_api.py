from fastapi.testclient import TestClient
from main import app
from models import Category

client = TestClient(app)
API_KEY = "supersecretkey"


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_create_defect():
    payload = {"title": "Test arıza", "category": Category.mekanik.value}
    r = client.post("/defect", json=payload, headers={"x-api-key": API_KEY})
    print(">> /defect POST STATUS:", r.status_code)
    print(">> /defect POST RESPONSE:", r.json())
    assert r.status_code == 200
    data = r.json()
    assert "title" in data
    assert data["title"] == "Test arıza"


def test_list_defects():
    r = client.get("/defect")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_stats():
    r = client.get("/stats", headers={"x-api-key": API_KEY})
    assert r.status_code == 200
    stats = r.json()
    assert "total_defects" in stats
    assert "open_defects" in stats
    assert "resolved_defects" in stats
