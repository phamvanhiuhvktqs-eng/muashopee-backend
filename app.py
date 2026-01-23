from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import urllib.parse
import os

app = Flask(__name__)

# CORS chuẩn cho Firebase web.app
CORS(app, resources={r"/*": {"origins": "*"}})

AFFILIATE_LINK = "https://s.shopee.vn/6KyNy3OYeP"

# ✅ Route test bắt buộc
@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "muashopee-backend-railway"
    })

# ✅ API convert
@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL"}), 400

    original_url = data["url"]
    encoded = urllib.parse.quote(original_url, safe="")

    # ✅ Tự động lấy domain hiện tại (Railway)
    base_url = request.host_url.rstrip("/")
    final_link = f"{base_url}/go?target={encoded}"

    return jsonify({
        "affiliate_url": final_link
    })

# ✅ Redirect + gắn affiliate
@app.route("/go")
def go():
    target = request.args.get("target")
    if not target:
        return jsonify({"error": "Missing target"}), 400

    response = redirect(AFFILIATE_LINK, code=302)

    # Shopee sẽ redirect tiếp sau 1s
    response.headers["Refresh"] = f"1; url={target}"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
