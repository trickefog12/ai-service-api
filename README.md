# AI-as-a-Service Image Analysis API (FastAPI + Stripe + Google Vision)

[![Python CI](https://github.com/trickefog12/ai-service-api/actions/workflows/ci.yml/badge.svg)](https://github.com/trickefog12/ai-service-api/actions/workflows/ci.yml)

A SaaS seed / MVP backend API that delivers AI-powered image analysis **only after successful payment verification** via Stripe. After payment, the system issues an **API key** that unlocks the AI analysis endpoint.

## 🚀 Overview

This project implements an end-to-end “payment → entitlement → AI” workflow:

1. User initiates payment via **Stripe Checkout**.
2. Stripe calls a **webhook** on successful payment.
3. The webhook stores the payment record and generates a unique **API key**.
4. User calls the AI endpoint with an `X-API-Key` header to access **Google Vision AI** analysis.

The system ensures that **only paying users** can access the AI functionality.

---

## 🧠 Features

- ✅ **Secure Payments**: Stripe Checkout session creation (`POST /create-checkout`).
- ✅ **Webhook Integration**: Stripe webhook verification with idempotent processing (`POST /webhook`).
- ✅ **Key-Based Access**: API key issuance on payment completion, stored securely in the database.
- ✅ **AI Paywall**: AI endpoint (`POST /analyze-image`) protected by custom header authentication.
- ✅ **Vision AI**: Automated label detection using Google Cloud Vision API.
- ✅ **Persistence**: Database management via **SQLAlchemy** (SQLite for dev, PostgreSQL ready).
- ✅ **CI/CD Ready**: Automated testing with **Pytest** and **GitHub Actions**.

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python), Uvicorn |
| **Database** | SQLAlchemy (SQLite default; configurable via `DATABASE_URL`) |
| **Payments** | Stripe API + Webhooks |
| **AI Service** | Google Cloud Vision API |
| **Testing / CI** | Pytest + GitHub Actions |

---

## 🔐 Auth & Paywall Model

- The AI endpoint requires an API key sent as an HTTP header:
  - Header: `X-API-Key: <your_api_key>`
- **Errors**:
  - `403 Forbidden`: Missing or invalid API key.
  - `500 Internal Server Error`: Vision API or processing failure.

---

## 🏗️ Architecture

```text
Client → POST /create-checkout → Stripe Checkout Page
                                        ↓
                              Stripe Webhook Event
                                        ↓
                      Database (SQLAlchemy) — stores payment + API key
                                        ↓
                 Client → POST /analyze-image (X-API-Key auth)
                                        ↓
                           Google Cloud Vision API (labels)
---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/create-checkout` | Creates Stripe payment session |
| POST | `/webhook` | Receives Stripe payment confirmation |
| POST | `/analyze-image` | AI analysis (paying users only) |
| GET | `/payments` | List all payments |
| GET | `/success` | Payment success redirect |
| GET | `/cancel` | Payment cancel redirect |

---

## 🔐 Payment & Paywall Flow

1. **POST /create-checkout**: Returns a Stripe-hosted URL to the user.
2. **POST /webhook**: Called automatically by Stripe upon payment. It verifies the signature and stores the user's email in the database.
3. **POST /analyze-image**: Checks the database first. If the email doesn't have a record, it returns a `402 Payment Required` error.

---

## 🧪 Local Setup & Testing

### 1. Create environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configure environment variables
Create a `.env` file:
```text
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
DATABASE_URL=sqlite:///./sql_app.db
# Local dev only (not needed on Cloud Run)
GOOGLE_APPLICATION_CREDENTIALS=keys/gcp-service-account.json
```

### 3. Start the API (Terminal 1)
```bash
uvicorn main:app --reload
```

### 4. Start Stripe listener (Terminal 2)
```bash
stripe listen --forward-to localhost:8000/webhook
```

### 5. Trigger test payment (Terminal 3)
```bash
stripe trigger checkout.session.completed
```
---

## 🔍 Usage Examples (cURL)
###Analyze an Image
{
curl -X POST "http://127.0.0.1:8000/analyze-image" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -F "file=@/path/to/image.jpg"
}

---

## 🔍 Example Response

```json
{
  "user": "customer@example.com",
  "labels": ["Sky", "Mountain", "Nature"],
  "message": "Analysis successful. Thank you for your payment!"
}
```

---

## ☁️ Deployment (Google Cloud Run)
Google Vision Credentials
In production (Cloud Run), the application uses Application Default Credentials (ADC).
• Do NOT upload credential JSON files to the container.
• Attach a Service Account to the Cloud Run service with the Cloud Vision API User role.
• The vision.ImageAnnotatorClient() in the code is configured to initialize lazily for optimal cold-start performance.

---

## ✅ Production Roadmap
☐ Implement transactional emails (SendGrid/Postmark) to deliver API keys to users.
☐ Migrate from SQLite to a managed PostgreSQL instance for production data.
☐ Add rate limiting per API key to prevent abuse.
☐ Move secrets (Stripe Keys) from .env to Google Secret Manager.

---

## 💡 Key Learnings

- Handling real-world payment flows using webhooks.
- Securing APIs with paywall logic.
- Integrating third-party AI services (Google Cloud Vision).
- Debugging SDK objects vs Python dictionaries.
- Building production-ready SaaS backend systems.

---

## 👨‍💻 Author

**Christos Vatistas**
AI Software Engineer & Backend Developer
[GitHub Profile](https://github.com/trickefog12)
