from flask import Flask, request, jsonify, redirect
import requests
import re
from urllib.parse import urlparse, unquote

app = Flask(__name__)

# ===============================
# FOLLOW REDIRECT (shp.ee)
# ===============================
def resolve_redirect(url):
    try:
        for _ in range(5):
            r = requests.head(url, allow_redirects=False, timeout=5)
            if "Location" not in r.headers:
                break
            url = r.headers["Location"]
        return url
    except:
        return url


# ===============================
# CHUẨN HÓA LINK SHOPEE
# ===============================
def normalize_shopee_link(input_url: str) -> str:
    if not input_url:
        raise ValueError("Link rỗng")

    url = input_url.strip()

    # decode nếu bị encode
    try:
        url = unquote(url)
    except:
        pass

    # link rút gọn
    if "shp.ee" in url:
        url = resolve_redirect(url)

    parsed = urlparse(url)
    path = parsed.path

    # CASE 1: /product/SHOP_ID/ITEM_ID
    m = re.search(r"/product/(\d+)/(\d+)", path)
    if m:
        shop_id, item_id = m.groups()
        return f"https://shopee.vn/product/{shop_id}/{item_id}"

    # CASE 2: /i.SHOP_ID.ITEM_ID
    m = re.search(r"/i\.(\d+)\.(\d+)", path)
    if m:
        shop_id, item_id = m.groups()
        return f"https://shopee.vn/product/{shop_id}/{item_id}"

    # CASE 3: link app có smtt / utm → bỏ query xử lại
    if parsed.query:
        clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path
        return normalize_shopee_link(clean_url)

    # KHÔNG PHẢI LINK SẢN PHẨM
    raise ValueError("Không phải link sản phẩm Shopee hợp lệ")


# ===============================
# API TEST
# ===============================
@app.route("/normalize")
def normalize():
    link = request.args.get("url", "")
    try:
        normalized = normalize_shopee_link(link)
        return jsonify({
            "success": True,
            "normalized": normalized
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ===============================
# CHẠY APP
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
