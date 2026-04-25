from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scanner import scan_article
from database import init_db, save_result, get_all_results
import os
from dotenv import load_dotenv
load_dotenv()
print("🔑 GEMINI KEY:", "Loaded" if os.getenv("GEMINI_API_KEY") else "❌ MISSING")

app = FastAPI(title="Deepfake Detector API")

# INIT DATABASE
init_db()

# CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# REQUEST MODEL
class ScanRequest(BaseModel):
    url: str


# HOME
@app.get("/")
def home():
    return {"message": "API Running ✅"}


# SCAN API
@app.post("/scan")
def scan(data: ScanRequest):
    try:
        print("🔗 Scanning:", data.url)

        result = scan_article(data.url)
        print("RESULT:", result)

        # ALWAYS SAVE (remove condition for debugging)
        save_result(result)

        print("Saved to DB")

        return result

    except Exception as e:
        print("Scan error:", e)

        return {
            "title": "Error",
            "image_score": 0,
            "text_score": 0,
            "final_score": 0,
            "confidence": 0,
            "verdict": "Error",
            "analysis": str(e)
        }


# HISTORY API
@app.get("/history")
def history():
    try:
        data = get_all_results()
        print("HISTORY:", data)
        return data

    except Exception as e:
        print("History error:", e)
        return []