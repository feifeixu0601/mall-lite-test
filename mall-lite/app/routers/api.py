"""
MallLite API 路由
提供 RESTful JSON 接口，供自动化测试调用
"""

from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/api")


def get_store(request: Request):
    """从 app state 获取 DataStore 实例"""
    return request.app.state.store


# ====== 用户接口 ======

@router.post("/login")
async def api_login(request: Request):
    body = await request.json()
    store = get_store(request)
    result = store.verify_login(body.get("username", ""), body.get("password", ""))
    if not result["success"]:
        return {"code": 401, "message": result["message"], "data": None}
    return {"code": 200, "message": result["message"], "data": result["user"]}


@router.post("/register")
async def api_register(request: Request):
    body = await request.json()
    store = get_store(request)
    username = body.get("username", "")
    password = body.get("password", "")

    if not username or not password:
        return {"code": 400, "message": "用户名和密码不能为空", "data": None}

    if store.get_user_by_username(username):
        return {"code": 400, "message": "用户名已存在", "data": None}

    return {"code": 200, "message": "注册成功", "data": {"username": username}}


# ====== 商品接口 ======

@router.get("/products")
async def api_products(request: Request, page: int = 1, page_size: int = 10,
                        category: str = None, keyword: str = None):
    store = get_store(request)

    if keyword:
        products = store.search_products(keyword)
    elif category:
        products = store.get_products_by_category(category)
    else:
        products = store.get_products()

    total = len(products)
    start = (page - 1) * page_size
    items = [p.to_dict() for p in products[start:start + page_size]]

    return {
        "code": 200,
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "items": items,
        }
    }


@router.get("/products/search")
async def api_search(request: Request, q: str = ""):
    store = get_store(request)
    if not q:
        return {"code": 200, "data": {"items": [], "total": 0}}
    results = store.search_products(q)
    return {
        "code": 200,
        "data": {"items": [p.to_dict() for p in results], "total": len(results)}
    }


@router.get("/products/{product_id}")
async def api_product_detail(request: Request, product_id: int):
    store = get_store(request)
    product = store.get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"code": 200, "data": product.to_dict()}


@router.get("/categories")
async def api_categories(request: Request):
    store = get_store(request)
    return {"code": 200, "data": store.get_categories()}


# ====== 购物车接口 ======

@router.get("/cart")
async def api_get_cart(request: Request, user_id: int = 2):
    store = get_store(request)
    cart = store.get_cart(user_id)
    summary = store.get_cart_total(user_id)
    return {
        "code": 200,
        "data": {
            "items": [item.to_dict() for item in cart],
            **summary,
        }
    }


@router.post("/cart")
async def api_add_to_cart(request: Request):
    body = await request.json()
    store = get_store(request)
    result = store.add_to_cart(
        user_id=body.get("user_id", 2),
        product_id=body.get("product_id"),
        quantity=body.get("quantity", 1),
    )
    code = 200 if result["success"] else 400
    return {"code": code, "message": result["message"]}


@router.put("/cart/{product_id}")
async def api_update_cart(request: Request, product_id: int):
    body = await request.json()
    store = get_store(request)
    result = store.update_cart_quantity(
        user_id=body.get("user_id", 2),
        product_id=product_id,
        quantity=body.get("quantity", 1),
    )
    code = 200 if result["success"] else 400
    return {"code": code, "message": result["message"]}


@router.delete("/cart/{product_id}")
async def api_remove_from_cart(request: Request, product_id: int, user_id: int = 2):
    store = get_store(request)
    result = store.remove_from_cart(user_id, product_id)
    code = 200 if result["success"] else 400
    return {"code": code, "message": result["message"]}


# ====== 订单接口 ======

@router.get("/orders")
async def api_orders(request: Request, user_id: int = 2, status: str = None):
    store = get_store(request)
    orders = store.get_orders_by_user(user_id)
    if status:
        orders = [o for o in orders if o["status"] == status]
    return {"code": 200, "data": {"items": orders, "total": len(orders)}}


@router.post("/orders")
async def api_create_order(request: Request):
    body = await request.json()
    store = get_store(request)
    user_id = body.get("user_id", 2)
    cart = store.get_cart(user_id)
    result = store.create_order(user_id, cart)
    code = 200 if result["success"] else 400
    return {"code": code, "message": result["message"], "data": result.get("order")}


@router.get("/orders/{order_no}")
async def api_order_detail(request: Request, order_no: str):
    store = get_store(request)
    order = store.get_order_by_no(order_no)
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return {"code": 200, "data": order}


@router.put("/orders/{order_no}/cancel")
async def api_cancel_order(request: Request, order_no: str):
    store = get_store(request)
    success = store.update_order_status(order_no, "已取消")
    if success:
        return {"code": 200, "message": f"订单 {order_no} 已取消"}
    return {"code": 400, "message": "取消失败"}