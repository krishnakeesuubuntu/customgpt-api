from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "data.db"

# Initialize the database and table
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS info_store (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/fetch", methods=["POST"])
def fetch():
    key = request.json.get("key")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM info_store WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        value = row[0]
        if len(value) > 1000:
            value = value[:1000] + " ... [truncated]"
        return jsonify({"result": value})
    return jsonify({"result": "No info found."})

@app.route("/add", methods=["POST"])
def add():
    key = request.json.get("key")
    value = request.json.get("value")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO info_store (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    return jsonify({"result": "Info added."})

@app.route("/modify", methods=["POST"])
def modify():
    key = request.json.get("key")
    value = request.json.get("value")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM info_store WHERE key = ?", (key,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"result": "Key not found."})
    cursor.execute("UPDATE info_store SET value = ? WHERE key = ?", (value, key))
    conn.commit()
    conn.close()
    return jsonify({"result": "Info updated."})

@app.route("/delete", methods=["POST"])
def delete():
    key = request.json.get("key")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM info_store WHERE key = ?", (key,))
    conn.commit()
    conn.close()
    return jsonify({"result": "Info deleted."})

@app.route('/list_keys', methods=['GET'])
def list_keys():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM info_store")
        rows = cursor.fetchall()
        keys = [row[0] for row in rows]
        conn.close()
        return jsonify({"keys": keys}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to retrieve keys"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
