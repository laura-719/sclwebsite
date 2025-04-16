from flask import Flask, render_template, request
from pathlib import Path
import pandas as pd

app = Flask(__name__)

# 🔹 자동 스캔된 제품 리스트 생성
def scan_products():
    base_path = Path("static/images")
    products = []
    for category_folder in base_path.iterdir():
        if category_folder.is_dir():
            for image_file in category_folder.glob("*.[jp][pn]g"):
                products.append({
                    "id": len(products),
                    "name": image_file.stem,
                    "filename": f"images/{category_folder.name}/{image_file.name}",
                    "category": category_folder.name
                })
    return products

# 🔹 제품 상세 설명 불러오기
def load_product_details():
    try:
        df = pd.read_excel("static/data/product_details.xlsx")
        return {
            row["id"]: {
                "features": row["features"],
                "electrical_spec": row["electrical_spec"],
                "environment_spec": row["environment_spec"]
            }
            for _, row in df.iterrows()
        }
    except Exception:
        return {}

ALL_PRODUCTS = scan_products()
DETAILS = load_product_details()
CATEGORIES = sorted(set((p["category"], p["category"]) for p in ALL_PRODUCTS))

# 🏠 홈
@app.route("/")
def home():
    return render_template("index.html", title="홈")

# 👋 회사 소개
@app.route("/company/greeting")
def company_greeting():
    return render_template("company/greeting.html", title="인사말", section="COMPANY")

@app.route("/company/organization")
def company_organization():
    return render_template("company/organization.html", title="조직도", section="COMPANY")

@app.route("/company/location")
def company_location():
    return render_template("company/location.html", title="찾아오시는 길", section="COMPANY")

@app.route("/business")
def business():
    return render_template("business.html", title="사업영역", section="BUSINESS")

# 📦 제품 소개
@app.route("/products")
def products():
    page = int(request.args.get("page", 1))
    keyword = request.args.get("q", "").lower()
    category = request.args.get("cat", "")

    filtered = [
        p for p in ALL_PRODUCTS
        if keyword in p["name"].lower() and (category == "" or p["category"] == category)
    ]

    per_page = 9
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(filtered) + per_page - 1) // per_page

    return render_template(
        "products.html",
        products=filtered[start:end],
        page=page,
        total_pages=total_pages,
        current_category=category,
        keyword=keyword,
        categories=CATEGORIES,
        section="PRODUCT",
        title="제품소개"
    )

# 🧾 제품 상세
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = next((p for p in ALL_PRODUCTS if p["id"] == product_id), None)
    if not product:
        return "Product not found", 404
    details = DETAILS.get(product_id, {})
    return render_template("product_detail.html", product=product, details=details, section="PRODUCT", title="제품 상세")

# 🛠 서비스
@app.route("/service/notice")
def service_notice():
    return render_template("service/notice.html", title="공지사항", section="SERVICE")

@app.route("/service/qna")
def service_qna():
    return render_template("service/qna.html", title="문의게시판", section="SERVICE")

