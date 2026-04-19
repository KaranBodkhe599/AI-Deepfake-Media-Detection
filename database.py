import sqlite3;
DB_NAME = "results.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        image_score REAL,
        text_score REAL,
        final_score REAL,
        verdict TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_result(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO scans (title, image_score, text_score, final_score, verdict)
    VALUES (?, ?, ?, ?, ?)
    """, (
        data["title"],
        data["image_score"],
        data["text_score"],
        data["final_score"],
        data["verdict"]
    ))

    conn.commit()
    conn.close()

def get_all_results():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scans ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows