import os
from fastapi import FastAPI, HTTPException, UploadFile, File
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
async def analyze_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        image = vision.Image(content=content)
        response = vision_client.label_detection(image=image)
        labels = [label.description for label in response.label_annotations]
        return {"labels": labels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))