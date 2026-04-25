import sqlite3
import os

# FIXED PATH (absolute path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "deepfake.db")


# GET CONNECTION
def get_conn():
    print("Using DB:", DB_PATH)  
    return sqlite3.connect(DB_PATH)


# INIT DB
def init_db():
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            image_score REAL,
            text_score REAL,
            final_score REAL,
            verdict TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

        print("Database ready")

    except Exception as e:
        print("DB INIT ERROR:", e)


# SAVE RESULT
def save_result(data):
    conn = None
    try:
        print("Saving:", data)

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO scans (title, image_score, text_score, final_score, verdict)
        VALUES (?, ?, ?, ?, ?)
        """, (
            str(data.get("title", "No Title")),
            float(data.get("image_score", 0)),
            float(data.get("text_score", 0)),
            float(data.get("final_score", 0)),
            str(data.get("verdict", "Unknown"))
        ))

        conn.commit()

        print("Saved to SQLite")

    except Exception as e:
        print("SAVE ERROR:", e)

    finally:
        if conn:
            conn.close()


# FETCH HISTORY
def get_all_results():
    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, title, image_score, text_score, final_score, verdict
        FROM scans
        ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        results = [
            {
                "id": r[0],
                "title": r[1],
                "image_score": r[2],
                "text_score": r[3],
                "final_score": r[4],
                "verdict": r[5]
            }
            for r in rows
        ]

        print("Fetched rows:", results)  # 🔥 DEBUG

        return results

    except Exception as e:
        print("FETCH ERROR:", e)
        return []

    finally:
        if conn:
            conn.close()