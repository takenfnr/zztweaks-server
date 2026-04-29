from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
import uuid
import os

app = Flask(__name__)

# =========================
# 🔐 MONGO CONFIG
# =========================

# 👉 Sätt din connection string som ENV VAR i Render (rekommenderas)
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI saknas! Lägg till i Render Environment Variables.")

client = MongoClient(MONGO_URI)

db = client["zztweaks"]
keys_col = db["keys"]

# =========================
# 🔑 CHECK KEY (HWID LOCK)
# =========================
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    if not key or not hwid:
        return jsonify({"status": "error"})

    k = keys_col.find_one({"key": key})

    if not k:
        return jsonify({"status": "invalid"})

    # första användning → bind HWID
    if not k.get("hwid"):
        keys_col.update_one(
            {"key": key},
            {"$set": {"hwid": hwid}}
        )
        return jsonify({"status": "ok"})

    # samma dator
    if k["hwid"] == hwid:
        return jsonify({"status": "ok"})

    # annan dator
    return jsonify({"status": "locked"})

# =========================
# ➕ CREATE KEY
# =========================
@app.route("/create")
def create():
    key = str(uuid.uuid4())[:16]

    keys_col.insert_one({
        "key": key,
        "hwid": ""
    })

    return f"""
    <h2>New Key:</h2>
    <p>{key}</p>
    <a href="/">Back</a>
    """

# =========================
# ❌ DELETE KEY
# =========================
@app.route("/delete/<key>")
def delete(key):
    keys_col.delete_one({"key": key})

    return """
    <h3>Deleted</h3>
    <a href="/">Back</a>
    """

# =========================
# 🎛️ ADMIN PANEL
# =========================
@app.route("/")
def panel():
    all_keys = list(keys_col.find())

    html = """
    <h1>ZZTweaks Panel</h1>

    <form action="/create">
        <button>Create Key</button>
    </form>

    <h3>Keys:</h3>
    <ul>
    {% for k in keys %}
        <li>
            <b>{{k.key}}</b> |
            {{k.hwid if k.hwid else "NOT USED"}}
            <a href="/delete/{{k.key}}">[Delete]</a>
        </li>
    {% endfor %}
    </ul>
    """

    return render_template_string(html, keys=all_keys)

# =========================
# 🚀 START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
