from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_love_yourself():
    response = client.get("/kiss", headers={"accept": "application/json"})
    assert response.status_code == 200
    assert response.json() == "Secret kisses for you <3"


def test_love_yourself2():
    response = client.get("/", headers={"accept": "application/json"})
    assert response.status_code == 200
    assert response.json() == "Double secret kisses for you <3"
