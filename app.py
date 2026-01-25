from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse
import os

app = Flask(__name__)
CORS(app)

# Affiliate ID của bạn
AFFILIATE_ID = "17313960485"
SUB_ID = "muashopee"

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json(silent=True) or {}
    shopee_url = data.get("url", "").strip()

    if not shopee_url:
        return jsonify({"error": "Missing Shopee URL"}), 400

    # ⚠️ CHUẨN SHOPEE: CHỈ CHẤP NHẬN LINK shopee.vn
    if "shopee.vn" not in shopee_url:
        return jsonify({
            "error": "Shopee chỉ hỗ trợ link gốc dạng https://shopee.vn/..."
        }), 400

    # BƯỚC 2: URL ENCODE LINK ĐÍCH
    encoded_url = urllib.parse.quote(shopee_url, safe="")

    # BƯỚC 3 + 4: TẠO LINK AFFILIATE THEO SHOPEE
    affiliate_link = (
        "https://s.shopee.vn/an_redir"
        "?origin_link=" + encoded_url +
        "&affiliate_id=" + AFFILIATE_ID +
        "&sub_id=" + SUB_ID
    )

    # ⚠️ KHÔNG gọi Shopee
    # ⚠️ KHÔNG decode
    # ⚠️ KHÔNG tạo short link
    # → Trả đúng link Shopee hướng dẫn

    return jsonify({
        "affiliate_url": affiliate_link
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
