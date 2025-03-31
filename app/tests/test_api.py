from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hello():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from SayItNative!"}


def test_non_existing_endpoint():
    response = client.get('/non-existing-endpoint')
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
