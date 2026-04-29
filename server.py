from flask import Flask, request, jsonify
import json
import os
import uuid

app = Flask(__name__)

DB_FILE = "keys.json"

# skapa fil om den inte finns
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===== CHECK KEY =====
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    db = load_db()

    if key not in db:
        return jsonify({"status": "invalid"})

    # första gången → lås key till HWID
    if db[key] == "":
        db[key] = hwid
        save_db(db)
        return jsonify({"status": "ok"})

    # samma dator → ok
    if db[key] == hwid:
        return jsonify({"status": "ok"})

    # annan dator → block
    return jsonify({"status": "locked"})

# ===== CREATE KEY =====
@app.route("/create")
def create():
    key = str(uuid.uuid4())[:16]

    db = load_db()
    db[key] = ""
    save_db(db)

    return jsonify({"key": key})

# ===== DELETE KEY =====
@app.route("/delete/<key>")
def delete(key):
    db = load_db()

    if key in db:
        del db[key]
        save_db(db)
        return jsonify({"status": "deleted"})

    return jsonify({"status": "not_found"})

# ===== START SERVER =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
