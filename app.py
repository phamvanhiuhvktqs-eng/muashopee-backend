from flask import Flask, request, jsonify
import urllib.parse
import requests
import os

app = Flask(__name__)

AFFILIATE_ID = "17313960485"
SUB_ID = "muashopee"

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    raw_url = data.get("url", "").strip()

    if not raw_url:
        return jsonify({"error": "Missing url"}), 400

    encoded = urllib.parse.quote(raw_url, safe="")

    an_redir = (
        "https://s.shopee.vn/an_redir"
        f"?origin_link={encoded}"
        f"&affiliate_id={AFFILIATE_ID}"
        f"&sub_id={SUB_ID}"
    )

    # 🔥 BẮT BUỘC: gọi Shopee để nó tạo short link mới
    r = requests.get(
        an_redir,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        },
        allow_redirects=False,
        timeout=10
    )

    # ƯU TIÊN Location (302)
    short_link = r.headers.get("Location")

    # Fallback: nếu Shopee không trả Location
    if not short_link:
        short_link = an_redir

    return jsonify({
        "affiliate_url": short_link
    })

@app.route("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
