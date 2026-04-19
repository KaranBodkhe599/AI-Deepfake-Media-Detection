from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scanner import scan_article
from database import init_db, save_result, get_all_results

app = FastAPI()

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API Running "}

@app.post("/scan")
def scan(data: dict):
    try:
        url = data.get("url")

        if not url:
            return {"error": "No URL provided"}

        print("🔗 URL:", url)

        result = scan_article(url)

        print("RESULT:", result)

        save_result(result)

        return result

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "title": "Error",
            "image_score": 0,
            "text_score": 0,
            "final_score": 0,
            "verdict": "Error"
        }

@app.get("/history")
def history():
    rows = get_all_results()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "title": r[1],
            "image_score": r[2],
            "text_score": r[3],
            "final_score": r[4],
            "verdict": r[5]
        })
    return results