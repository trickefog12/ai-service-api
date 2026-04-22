# AI Service API (FastAPI + Google Vision + Stripe)

Backend API that:
- Creates Stripe Checkout sessions to gate access (payments)
- Analyzes uploaded images using Google Cloud Vision API and returns detected labels

## Tech Stack
- Python, FastAPI, Uvicorn
- Stripe API (Checkout)
- Google Cloud Vision API
- dotenv / environment variables

## End-to-end flow
1) Client calls `POST /create-checkout` -> backend creates Stripe Checkout Session and returns a checkout URL
2) After payment, client calls `POST /analyze-image` with an image -> backend sends it to Google Vision API -> returns labels

## Setup (local)
### 1) Create a virtual environment (Conda)
```bash
conda create -n ai-service-api python=3.11 -y
conda activate ai-service-api
pip install -r requirements.txt
