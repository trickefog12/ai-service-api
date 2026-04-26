from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Ελέγχει αν η αρχική σελίδα λειτουργεί"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Service API is running!"}

def test_success_page():
    """Ελέγχει αν η σελίδα επιτυχίας λειτουργεί"""
    response = client.get("/success")
    assert response.status_code == 200
    assert "Payment successful" in response.json()["message"]

def test_create_checkout_success(mocker):
    """Ελέγχει αν το checkout δημιουργείται σωστά (χωρίς πραγματικό Stripe)"""
    mock_session = mocker.MagicMock()
    mock_session.url = "https://checkout.stripe.com/fake-url"
    
    mocker.patch("stripe.checkout.Session.create", return_value=mock_session)
    
    response = client.post("/create-checkout")
    
    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["url"] == "https://checkout.stripe.com/fake-url"