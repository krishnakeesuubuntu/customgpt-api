from flask import Flask, request, jsonify
import os
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Connect to PostgreSQL
def get_db_connection():
    result = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    return conn

# Create table if not exists
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS info_store (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route("/fetch", methods=["POST"])
def fetch():
    key = request.json.get("key")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM info_store WHERE key = %s", (key,))
    row = cur.fetchone()
    cur.close()
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO info_store (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value", (key, value))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"result": "Info added."})

@app.route("/modify", methods=["POST"])
def modify():
    key = request.json.get("key")
    value = request.json.get("value")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM info_store WHERE key = %s", (key,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"result": "Key not found."})
    cur.execute("UPDATE info_store SET value = %s WHERE key = %s", (value, key))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"result": "Info updated."})

@app.route("/delete", methods=["POST"])
def delete():
    key = request.json.get("key")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM info_store WHERE key = %s", (key,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"result": "Info deleted."})

@app.route('/list_keys', methods=['GET'])
def list_keys():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT key FROM info_store")
        rows = cur.fetchall()
        keys = [row[0] for row in rows]
        cur.close()
        conn.close()
        return jsonify({"keys": keys}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to retrieve keys"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
