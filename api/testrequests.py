import requests

# 用 Session 自动管理 Cookie
session = requests.Session()

# ========================================
# GET 请求
# ========================================
response = session.get("http://localhost:8000/api/products")
print(response.status_code)        # 200
print(response.json())             # {"code": 200, "data": {"items": [...]}}

# ========================================
# POST 请求 - 登录
# ========================================
response = session.post(
    "http://localhost:8000/api/login",
    json={"username": "admin", "password": "admin123"}
)
print(response.status_code)        # 200
data = response.json()
print(data)                        # {"code": 200, "message": "登录成功", "data": {...}}

# MallLite 用 Session + Cookie 认证，不用 Token
# 登录后 Cookie 自动保存在 session 里，后续请求自动带上

# ========================================
# GET 带认证
# ========================================
response = session.get(
    "http://localhost:8000/api/cart"
)
print(response.json())

# ========================================
# POST 带认证
# ========================================
response = session.post(
    "http://localhost:8000/api/cart",
    json={"product_id": 1, "quantity": 2}
)
print(response.json())

# ========================================
# PUT 请求
# ========================================
response = session.put(
    "http://localhost:8000/api/cart/1",
    json={"quantity": 3}
)
print(response.json())

# ========================================
# DELETE 请求
# ========================================
response = session.delete(
    "http://localhost:8000/api/cart/1"
)
print(response.json())