from flask import Flask, request, jsonify, render_template_string
import json
import os
import uuid

app = Flask(__name__)

DB_FILE = "keys.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===== CHECK =====
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    db = load_db()

    if key not in db:
        return jsonify({"status": "invalid"})

    if db[key] == "":
        db[key] = hwid
        save_db(db)
        return jsonify({"status": "ok"})

    if db[key] == hwid:
        return jsonify({"status": "ok"})

    return jsonify({"status": "locked"})

# ===== ADMIN PANEL =====
@app.route("/")
def panel():
    db = load_db()

    html = """
    <h1>ZZTweaks Key Panel</h1>

    <form action="/create" method="get">
        <button type="submit">Create Key</button>
    </form>

    <h2>Keys:</h2>
    <ul>
    {% for key, hwid in db.items() %}
        <li>
            <b>{{key}}</b> | HWID: {{hwid if hwid else "NOT USED"}}
            <a href="/delete/{{key}}">[Delete]</a>
        </li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, db=db)

# ===== CREATE =====
@app.route("/create")
def create():
    key = str(uuid.uuid4())[:16]

    db = load_db()
    db[key] = ""
    save_db(db)

    return f"<h2>New Key:</h2><p>{key}</p><a href='/'>Back</a>"

# ===== DELETE =====
@app.route("/delete/<key>")
def delete(key):
    db = load_db()

    if key in db:
        del db[key]
        save_db(db)

    return "<h3>Deleted</h3><a href='/'>Back</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
