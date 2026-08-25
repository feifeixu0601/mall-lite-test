"""
MallLite 页面路由
返回 HTML 页面，供 Playwright UI 测试使用
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "templates"))


def get_store(request: Request):
    return request.app.state.store


# ====== 首页 ======

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, page: int = 1, category: str = None, keyword: str = None):
    store = get_store(request)

    if keyword:
        products = store.search_products(keyword)
    elif category:
        products = store.get_products_by_category(category)
    else:
        products = store.get_products()

    page_size = 8
    total = len(products)
    total_pages = max((total + page_size - 1) // page_size, 1)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    page_products = products[start:start + page_size]

    categories = store.get_categories()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "products": page_products,
        "categories": categories,
        "current_category": category,
        "keyword": keyword or "",
        "page": page,
        "total_pages": total_pages,
        "total": total,
    })


# ====== 登录页 ======

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
    })


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(default=""), password: str = Form(default="")):
    store = get_store(request)
    result = store.verify_login(username, password)
    if result["success"]:
        response = RedirectResponse("/", status_code=302)
        response.set_cookie("username", username)
        response.set_cookie("user_id", str(result["user"]["id"]))
        return response
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": result["message"],
        "username": username,
    })


# ====== 商品详情页 ======

@router.get("/products/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int):
    store = get_store(request)
    product = store.get_product_by_id(product_id)
    if product is None:
        return HTMLResponse("<h1>商品不存在</h1>", status_code=404)
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
    })


# ====== 购物车页 ======

@router.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    store = get_store(request)
    user_id = int(request.cookies.get("user_id", "2"))
    cart = store.get_cart(user_id)
    summary = store.get_cart_total(user_id)
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "cart": cart,
        "summary": summary,
    })


@router.post("/cart/add/{product_id}", response_class=HTMLResponse)
async def cart_add(request: Request, product_id: int):
    store = get_store(request)
    user_id = int(request.cookies.get("user_id", "2"))
    store.add_to_cart(user_id, product_id, 1)
    return RedirectResponse("/cart", status_code=302)


@router.post("/cart/remove/{product_id}", response_class=HTMLResponse)
async def cart_remove(request: Request, product_id: int):
    store = get_store(request)
    user_id = int(request.cookies.get("user_id", "2"))
    store.remove_from_cart(user_id, product_id)
    return RedirectResponse("/cart", status_code=302)


# ====== 订单页 ======

@router.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    store = get_store(request)
    user_id = int(request.cookies.get("user_id", "2"))
    orders = store.get_orders_by_user(user_id)
    return templates.TemplateResponse("orders.html", {
        "request": request,
        "orders": orders,
    })


@router.post("/orders/create", response_class=HTMLResponse)
async def create_order(request: Request):
    store = get_store(request)
    user_id = int(request.cookies.get("user_id", "2"))
    cart = store.get_cart(user_id)
    store.create_order(user_id, cart)
    return RedirectResponse("/orders", status_code=302)


# ====== 个人中心 ======

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    store = get_store(request)
    username = request.cookies.get("username", "")
    user = store.get_user_by_username(username)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
    })


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("username")
    response.delete_cookie("user_id")
    return response