from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import urllib.parse
import requests
import os

app = Flask(__name__)
CORS(app)

AFFILIATE_ID = "17313960485"
SUB_ID = "muashopee"

# =========================
# HTML TEST ĐƠN GIẢN
# =========================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Chuyển link Shopee Affiliate</title>
</head>
<body style="max-width:600px;margin:40px auto;font-family:Arial">
  <h2>Chuyển link Shopee → Affiliate</h2>
  <input id="url" style="width:100%;padding:10px" placeholder="Dán link Shopee (kể cả vn.shp.ee)">
  <button style="margin-top:10px;padding:10px;width:100%" onclick="go()">Chuyển link</button>

<script>
function go() {
  const url = document.getElementById("url").value.trim();
  if (!url) return alert("Nhập link");

  fetch("/convert", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  })
  .then(r => r.json())
  .then(d => {
    if (d.affiliate_url) {
      window.location.href = d.affiliate_url;
    } else {
      alert(d.error || "Lỗi");
    }
  });
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

# =========================
# HÀM RESOLVE LINK NGẦM
# =========================
def resolve_shopee_url(url: str) -> str | None:
    """
    Follow redirect để lấy link Shopee đích
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html"
        }
        r = requests.get(
            url,
            headers=headers,
            allow_redirects=True,
            timeout=10
        )

        final_url = r.url

        if "shopee.vn/" in final_url:
            return final_url

        return None
    except Exception:
        return None

# =========================
# API CONVERT
# =========================
@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL"}), 400

    input_url = data["url"].strip()

    # Resolve link ngầm (CHẤP NHẬN vn.shp.ee, s.shopee.vn, fb, tiktok)
    final_url = resolve_shopee_url(input_url)

    if not final_url:
        return jsonify({
            "error": "Không resolve được link Shopee đích"
        }), 400

    # Encode CHUẨN
    encoded = urllib.parse.quote(final_url, safe=":/?=&")

    affiliate_link = (
        "https://s.shopee.vn/an_redir"
        f"?origin_link={encoded}"
        f"&affiliate_id={AFFILIATE_ID}"
        f"&sub_id={SUB_ID}"
    )

    return jsonify({
        "final_url": final_url,
        "affiliate_url": affiliate_link
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
