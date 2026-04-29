from flask import Flask, request, jsonify, render_template_string
import sqlite3
import uuid

app = Flask(__name__)

# ===== DB SETUP =====
def get_db():
    return sqlite3.connect("keys.db")

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            hwid TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ===== CHECK =====
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT hwid FROM keys WHERE key=?", (key,))
    row = c.fetchone()

    if not row:
        return jsonify({"status": "invalid"})

    saved_hwid = row[0]

    if saved_hwid == "" or saved_hwid is None:
        c.execute("UPDATE keys SET hwid=? WHERE key=?", (hwid, key))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})

    if saved_hwid == hwid:
        conn.close()
        return jsonify({"status": "ok"})

    conn.close()
    return jsonify({"status": "locked"})

# ===== CREATE =====
@app.route("/create")
def create():
    key = str(uuid.uuid4())[:16]

    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO keys (key, hwid) VALUES (?, ?)", (key, ""))
    conn.commit()
    conn.close()

    return f"<h2>New Key:</h2><p>{key}</p><a href='/'>Back</a>"

# ===== DELETE =====
@app.route("/delete/<key>")
def delete(key):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM keys WHERE key=?", (key,))
    conn.commit()
    conn.close()

    return "<h3>Deleted</h3><a href='/'>Back</a>"

# ===== PANEL =====
@app.route("/")
def panel():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT key, hwid FROM keys")
    rows = c.fetchall()
    conn.close()

    html = """
    <h1>ZZTweaks Panel</h1>

    <form action="/create">
        <button>Create Key</button>
    </form>

    <ul>
    {% for key, hwid in rows %}
        <li>
            <b>{{key}}</b> | {{hwid if hwid else "NOT USED"}}
            <a href="/delete/{{key}}">[Delete]</a>
        </li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
