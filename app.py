from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import urllib.parse

app = Flask(__name__)
CORS(app)

# 🔥 LINK AFFILIATE SHOPEE CỦA BẠN
AFFILIATE_LINK = "https://s.shopee.vn/6KyNy3OYeP"

# ✅ API: tạo link hoàn tiền
@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    original_url = data.get("url") if data else None

    if not original_url:
        return jsonify({"error": "Missing URL"}), 400

    encoded = urllib.parse.quote(original_url, safe="")

    # 👉 DÙNG DOMAIN RENDER (KHÔNG NGROK)
    final_link = f"https://muashopee-backend.onrender.com/go?target={encoded}"

    return jsonify({
        "affiliate_url": final_link
    })


# ✅ Redirect trung gian để set cookie affiliate
@app.route("/go")
def go():
    target = request.args.get("target")
    if not target:
        return "Missing target", 400

    response = redirect(AFFILIATE_LINK, code=302)
    response.headers["Refresh"] = f"1; url={target}"
    return response


# ✅ Health check (Render rất thích cái này)
@app.route("/")
def health():
    return "OK"
