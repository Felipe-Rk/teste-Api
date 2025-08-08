from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_flow():
    r = client.post("/v1/users", json={"username": "alice", "email": "alice@test.com", "posts": 0})
    assert r.status_code == 201
    user = r.json()
    assert user["id"] > 0

    r = client.post("/v1/posts", json={"user_id": user["id"], "content": "Hello world"})
    assert r.status_code == 201
    post = r.json()
    assert post["content"] == "Hello world"

    r = client.post(f"/v1/posts/{post['id']}/like")
    assert r.status_code == 204

    r = client.get("/v1/posts/feed?limit=10&offset=0")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
