import os
import uuid
from database import SessionLocal, Payment
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from dotenv import load_dotenv
import stripe
from google.cloud import vision

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = FastAPI(title="AI Service API")
vision_client = vision.ImageAnnotatorClient()


@app.get("/")
def home():
    return {"message": "AI Service API is running!"}

@app.get("/success")
def success():
    return {"message": "Payment successful"}

@app.get("/cancel")
def cancel():
    return {"message": "Payment cancelled"}

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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-image")
async def analyze_image(email: str, file: UploadFile = File(...)):
    # 1. Έλεγχος στη βάση μας
    db = SessionLocal()
    payment = db.query(Payment).filter(Payment.email == email, Payment.status == "completed").first()
    db.close()

    if not payment:
        # Αν δεν βρεθεί πληρωμή, πετάμε σφάλμα
        raise HTTPException(
            status_code=402, 
            detail="Payment required. Please pay at /create-checkout first."
        )

    # 2. Αν υπάρχει πληρωμή, συνεχίζουμε στο Vision API
    try:
        content = await file.read()
        image = vision.Image(content=content)
        response = vision_client.label_detection(image=image)
        labels = [label.description for label in response.label_annotations]
        
        return {
            "user": email,
            "labels": labels,
            "message": "Analysis successful. Thank you for your payment!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
print(f"DEBUG: Webhook secret loaded: {STRIPE_WEBHOOK_SECRET}")

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session.customer_details.email if session.customer_details else None
        stripe_id = session.id
        amount = session.amount_total

        db = SessionLocal()
        new_payment = Payment(
            stripe_id=stripe_id,
            email=customer_email,
            amount=amount,
            status="completed"
        )
        db.add(new_payment)
        db.commit()
        db.close()
        print(f"✅ Payment Success for {customer_email}")

    return {"status": "success"}

@app.get("/payments")
def get_payments():
    db = SessionLocal()
    try:
        payments = db.query(Payment).all()
        return payments
    finally:
        db.close()