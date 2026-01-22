from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import urllib.parse
import time

app = Flask(__name__)
CORS(app)

# 🔥 DÁN 1 LINK SHOPE.EE DUY NHẤT CỦA BẠN VÀO ĐÂY
AFFILIATE_LINK = "https://s.shopee.vn/6KyNy3OYeP"

@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "Missing URL"}), 400

    encoded = urllib.parse.quote(original_url, safe="")
    # Link trung gian qua backend
    final_link = f"https://calmier-learnable-sima.ngrok-free.dev/go?target={encoded}"

    return jsonify({
        "affiliate_url": final_link
    })

@app.route("/go")
def go():
    target = request.args.get("target")
    if not target:
        return "Missing target", 400

    # 👉 BƯỚC 1: redirect qua affiliate để set cookie
    response = redirect(AFFILIATE_LINK, code=302)
    response.headers["Refresh"] = f"1; url={target}"
    return response

if __name__ == "__main__":
    app.run(port=5000, debug=True)
