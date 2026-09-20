from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_duplicate_payment_is_not_created():

    payload = {
        "payment_key": "test-checkout-001",
        "registration_id": "registration-001",
        "amount": 1000,
        "currency": "INR",
    }

    first_response = client.post(
        "/payments",
        json=payload,
    )

    second_response = client.post(
        "/payments",
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_payment = first_response.json()
    second_payment = second_response.json()

    assert first_payment["id"] == second_payment["id"]
    assert (
        first_payment["payment_key"]
        == second_payment["payment_key"]
    )