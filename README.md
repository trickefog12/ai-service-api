# AI-as-a-Service Image Analysis API

A production-ready backend API that delivers AI-powered image analysis **only after successful payment verification** using Stripe.

## 🚀 Overview

This project implements a complete SaaS payment + AI workflow:

1. User initiates payment via Stripe Checkout
2. Stripe sends a webhook event upon successful payment
3. Payment is stored in a local database
4. User gains access to AI-powered image analysis

The system ensures that **only paying users** can access the AI functionality.

---

## 🧠 Features

- ✅ Secure payment processing with Stripe Checkout
- ✅ Real-time webhook handling for payment verification
- ✅ Paywalled AI service (Google Vision API)
- ✅ RESTful API built with FastAPI
- ✅ Persistent storage using SQLite & SQLAlchemy
- ✅ End-to-end SaaS backend architecture

---

## 🏗️ Architecture

```text
Client → POST /create-checkout → Stripe Checkout Page
                                        ↓
                              Stripe Webhook Event
                                        ↓
                              Database (SQLite) — stores payment
                                        ↓
                         POST /analyze-image (Paywall Check)
                                        ↓
                              Google Cloud Vision API
                                        ↓
                              JSON Response with Labels
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python) |
| **Database** | SQLite + SQLAlchemy |
| **Payments** | Stripe API + Webhooks |
| **AI Service** | Google Cloud Vision API |
| **Config** | python-dotenv |
| **Testing** | Stripe CLI |

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
conda create -n ai-service-api python=3.11 -y
conda activate ai-service-api
pip install -r requirements.txt
```

### 2. Configure environment variables
Create a `.env` file:
```text
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
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

## 🔍 Example Response

```json
{
  "user": "stripe@example.com",
  "labels": ["Person", "Fitness", "Exercise", "Sport"],
  "message": "Analysis successful. Thank you for your payment!"
}
```

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
