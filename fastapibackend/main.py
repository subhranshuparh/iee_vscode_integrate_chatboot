from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Annotated
import pickle
import pandas as pd
import os

# Load env
from dotenv import load_dotenv
load_dotenv()

# Gemini SDK
import google.generativeai as genai

app = FastAPI(title="Mind Score + Chatbot API")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Load ML model ---------------- #
ml_model = None
try:
    with open("model_ieee.pkl", "rb") as f:
        ml_model = pickle.load(f)
except Exception as e:
    print("⚠️ Could not load ML model:", e)

# ---------------- Configure Gemini ---------------- #
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Please set GEMINI_API_KEY environment variable")

genai.configure(api_key=GEMINI_API_KEY)

# ---------------- Prediction Input ---------------- #
class PredictionInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=100)]
    Gender: Literal["Male", "Female"]
    Academic_Level: Literal["Undergraduate", "Graduate", "High School"]
    Country: str
    Avg_Daily_Usage_Hours: Annotated[float, Field(..., gt=0, lt=50)]
    Most_Used_Platform: Literal[
        "Instagram", "Twitter", "TikTok", "YouTube", "Facebook", "LinkedIn",
        "Snapchat", "LINE", "KakaoTalk", "VKontakte", "WhatsApp", "WeChat"
    ]
    Sleep_Hours_Per_Night: Annotated[float, Field(..., gt=1, lt=12)]
    Relationship_Status: Literal["In Relationship", "Single", "Complicated"]

@app.post("/predict")
def predict(data: PredictionInput):
    if ml_model is None:
        raise HTTPException(status_code=500, detail="Model not available")

    input_df = pd.DataFrame([{
        "Age": data.age,
        "Gender": data.Gender,
        "Academic_Level": data.Academic_Level,
        "Country": data.Country.strip().title(),
        "Avg_Daily_Usage_Hours": data.Avg_Daily_Usage_Hours,
        "Most_Used_Platform": data.Most_Used_Platform.strip().title(),
        "Sleep_Hours_Per_Night": data.Sleep_Hours_Per_Night,
        "Relationship_Status": data.Relationship_Status.strip().title(),
    }])

    try:
        prediction = ml_model.predict(input_df)[0]
        return {"prediction": prediction}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ---------------- Chatbot ---------------- #
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict] = None

@app.post("/chat")
async def chat_with_gemini(req: ChatRequest):
    # Build context-aware prompt
    parts = []
    if req.context:
        ctx_lines = [f"{k}: {v}" for k, v in req.context.items()]
        parts.append("User context:\n" + "\n".join(ctx_lines) + "\n")

    parts.append("User says:")
    parts.append(req.message)
    prompt = "\n".join(parts)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API call failed: {e}")

    return {"response": resp.text.strip()}
