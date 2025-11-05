import os
from models import Category

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("ok") is True

def test_create_defect(client):
    API_KEY = os.getenv("API_KEY", "supersecretkey")
    payload = {"title": "Test arıza", "category": Category.mekanik.value}
    r = client.post("/defect", json=payload, headers={"x-api-key": API_KEY})
    assert r.status_code in (200,201)
    data = r.json()
    assert data["title"] == "Test arıza"

def test_list_defects(client):
    r = client.get("/defect")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_stats(client):
    API_KEY = os.getenv("API_KEY", "supersecretkey")
    r = client.get("/stats", headers={"x-api-key": API_KEY})
    assert r.status_code == 200
    stats = r.json()
    assert "total_defects" in stats
