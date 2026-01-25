from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import urllib.parse

app = Flask(__name__)
CORS(app)

AFFILIATE_ID = "17313960485"
SUB_ID = "muashopee"

# =========================
# FRONTEND (HTML + JS)
# =========================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <title>Chuyển link Shopee Affiliate</title>
  <style>
    body { font-family: Arial; max-width: 600px; margin: 40px auto; }
    input, button { width: 100%; padding: 10px; margin-top: 10px; }
    button { cursor: pointer; }
    .note { color: #666; font-size: 14px; margin-top: 10px; }
  </style>
</head>
<body>
  <h2>Chuyển link Shopee → Affiliate</h2>

  <input id="inputUrl" placeholder="Dán link Shopee (vn.shp.ee / s.shopee.vn / shopee.vn)" />
  <button onclick="handleConvert()">Chuyển link</button>

  <p class="note">
    ⚠️ Link sẽ được xử lý bằng trình duyệt để tránh lỗi 403.
  </p>

<script>
async function resolveFinalUrl(url) {
  return new Promise((resolve, reject) => {
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = url;

    iframe.onload = () => {
      try {
        const finalUrl = iframe.contentWindow.location.href;
        document.body.removeChild(iframe);
        resolve(finalUrl);
      } catch (e) {
        document.body.removeChild(iframe);
        reject("Không resolve được link");
      }
    };

    document.body.appendChild(iframe);
  });
}

async function handleConvert() {
  const input = document.getElementById("inputUrl").value.trim();
  if (!input) {
    alert("Vui lòng nhập link");
    return;
  }

  try {
    // BƯỚC 1: resolve link bằng TRÌNH DUYỆT
    const finalUrl = await resolveFinalUrl(input);

    if (!finalUrl.startsWith("https://shopee.vn/")) {
      alert("Link sau resolve không phải shopee.vn");
      return;
    }

    // BƯỚC 2: gửi link ĐÍCH về backend
    const res = await fetch("/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: finalUrl })
    });

    const data = await res.json();
    if (!data.affiliate_url) {
      alert("Lỗi tạo link");
      return;
    }

    // BƯỚC 3: redirect TRỰC TIẾP (KHÔNG fetch)
    window.location.href = data.affiliate_url;

  } catch (err) {
    alert("Không xử lý được link");
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

# =========================
# BACKEND – CHỈ GẮN AFF
# =========================
@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL"}), 400

    final_url = data["url"].strip()

    # CHỈ CHẤP NHẬN LINK SHOPEE ĐÍCH
    if not final_url.startswith("https://shopee.vn/"):
        return jsonify({"error": "Invalid final Shopee URL"}), 400

    # Encode CHUẨN – KHÔNG encode 2 lần
    encoded_url = urllib.parse.quote(final_url, safe=":/?=&")

    affiliate_link = (
        "https://s.shopee.vn/an_redir"
        f"?origin_link={encoded_url}"
        f"&affiliate_id={AFFILIATE_ID}"
        f"&sub_id={SUB_ID}"
    )

    return jsonify({
        "affiliate_url": affiliate_link
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
