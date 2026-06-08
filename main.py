import os
import logging
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Header
from dotenv import load_dotenv
import stripe
from google.cloud import vision

from database import SessionLocal, Payment, generate_api_key

load_dotenv()

# Logging αντί για print (production standard)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# ΣΗΜΑΝΤΙΚΟ: Καμία αναφορά σε GOOGLE_APPLICATION_CREDENTIALS
# Το Cloud Run χρησιμοποιεί αυτόματα το attached Service Account
app = FastAPI(title="AI Service API")
_vision_client = None

def get_vision_client():
    global _vision_client
    if _vision_client is None:
        _vision_client = vision.ImageAnnotatorClient()
    return _vision_client


# DB session helper — αποφεύγει leaks
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "AI Service API is running!"}


@app.get("/success")
def success():
    return {"message": "Payment successful! Check your email for your API key."}


@app.get("/cancel")
def cancel():
    return {"message": "Payment cancelled."}


@app.post("/create-checkout")
def create_checkout():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": "AI Image Analysis"},
                    "unit_amount": 500,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://127.0.0.1:8000/success",
            cancel_url="http://127.0.0.1:8000/cancel",
        )
        return {"url": session.url}
    except Exception as e:
        logger.error(f"Checkout creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        logger.warning(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        stripe_id = session.get("id")
        customer_email = (
            session.get("customer_details", {}).get("email")
            if isinstance(session.get("customer_details"), dict)
            else getattr(session.get("customer_details"), "email", None)
        )
        amount = session.get("amount_total")

        with get_db() as db:
            # Idempotency: αγνοούμε duplicate events
            existing = db.query(Payment).filter(Payment.stripe_id == stripe_id).first()
            if existing:
                logger.info(f"Duplicate webhook event for {stripe_id}, skipping.")
                return {"status": "already processed"}

            new_api_key = generate_api_key()
            new_payment = Payment(
                stripe_id=stripe_id,
                email=customer_email,
                api_key=new_api_key,
                amount=amount,
                status="completed"
            )
            db.add(new_payment)
            db.commit()
            logger.info(f"Payment recorded for {customer_email}")
            # TODO: Στείλε email στον χρήστη με το new_api_key

    return {"status": "success"}


@app.post("/analyze-image")
async def analyze_image(
    x_api_key: str = Header(None, alias="X-API-Key"),
    file: UploadFile = File(...)
):
    if not x_api_key:
        raise HTTPException(status_code=403, detail="Missing API Key.")

    with get_db() as db:
        payment = db.query(Payment).filter(
            Payment.api_key == x_api_key,
            Payment.status == "completed"
        ).first()

    if not payment:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key.")

    try:
        content = await file.read()
        image = vision.Image(content=content)
        client = get_vision_client()
        response = client.label_detection(image=image)
        labels = [label.description for label in response.label_annotations]

        return {
            "user": payment.email,
            "labels": labels,
            "message": "Analysis successful. Thank you for your payment!"
        }
    except Exception as e:
        logger.error(f"Vision API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payments")
def get_payments():
    with get_db() as db:
        payments = db.query(Payment).all()
        return payments