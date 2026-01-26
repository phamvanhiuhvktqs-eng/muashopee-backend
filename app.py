from flask import Flask, request, jsonify, redirect
import requests
import re
from urllib.parse import urlparse, unquote, quote

app = Flask(__name__)

# ===============================
# CẤU HÌNH AFFILIATE (CỦA BẠN)
# ===============================
AFFILIATE_ID = "17313960485"
SUB_ID = "muasamshopee"

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

    # CASE 3: link app có query → bỏ query xử lại
    if parsed.query:
        clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path
        return normalize_shopee_link(clean_url)

    raise ValueError("Không phải link sản phẩm Shopee hợp lệ")


# ===============================
# TẠO LINK AFFILIATE HỢP LỆ
# ===============================
def build_affiliate_link(product_url: str) -> str:
    encoded_origin = quote(product_url, safe="")
    return (
        "https://s.shopee.vn/an_redir"
        f"?affiliate_id={AFFILIATE_ID}"
        f"&sub_id={SUB_ID}"
        f"&origin_link={encoded_origin}"
    )


# ===============================
# API TEST CHUẨN HÓA
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
# API REDIRECT AFFILIATE (DÙNG CHÍNH)
# ===============================
@app.route("/go")
def go():
    link = request.args.get("url", "")
    try:
        normalized = normalize_shopee_link(link)
        aff_link = build_affiliate_link(normalized)
        return redirect(aff_link, code=302)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ===============================
# CHẠY SERVER
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
