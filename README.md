# AI Service API

A backend API built with FastAPI that integrates Stripe for payments and Google Cloud Vision API for image analysis.

## Features
- Create Stripe Checkout sessions
- Upload an image and analyze it with Google Vision API
- Return image labels in JSON format
- Secure configuration using environment variables

## Tech Stack
- Python
- FastAPI
- Uvicorn
- Stripe API
- Google Cloud Vision API
- python-dotenv

## API Endpoints
### `POST /create-checkout`
Creates a Stripe Checkout session and returns a payment URL.

### `POST /analyze-image`
Accepts an uploaded image, sends it to Google Vision API, and returns detected labels.

## Local Setup

### 1. Create environment
```bash
conda create -n ai-service-api python=3.11 -y
conda activate ai-service-api
pip install -r requirements.txt