"""
MallLite 电商系统 - 核心业务函数
功能：商品查询、搜索、筛选、分页、购物车、用户验证
"""

import json
import os

# ========================================
# 第一步：加载数据
# ========================================
data_dir = "data"

def load_json(filename):
    """加载 JSON 数据文件"""
    filepath = os.path.join(data_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

products = load_json("products.json")
users = load_json("users.json")
categories = load_json("categories.json")

print(f"加载完成：{len(products)} 个商品，{len(users)} 个用户，{len(categories)} 个分类")
print("=" * 60)


# ========================================
# 第二步：商品查询函数
# ========================================

def get_product_by_id(product_id):
    """
    根据商品 ID 查询商品

    参数：
        product_id: 商品 ID

    返回：
        找到则返回商品字典，找不到返回 None
    """
    for p in products:
        if p["id"] == product_id:
            return p
    return None


def get_products_by_category(category):
    """
    根据分类名称获取商品列表

    参数：
        category: 分类名称（如 "手机"）

    返回：
        该分类下的所有商品列表
    """
    result = []
    for p in products:
        if p["category"] == category:
            result.append(p)
    return result


def get_new_products():
    """获取所有新品"""
    result = []
    for p in products:
        if p["is_new"]:
            result.append(p)
    return result


def get_products_by_price_range(min_price, max_price):
    """
    按价格区间筛选商品

    参数：
        min_price: 最低价格
        max_price: 最高价格

    返回：
        价格在区间内的商品列表
    """
    result = []
    for p in products:
        if min_price <= p["price"] <= max_price:
            result.append(p)
    return result


# 测试查询函数
print("【商品查询】")
print("-" * 60)

product = get_product_by_id(1)
print(f"ID=1 的商品：{product['name']}（¥{product['price']}）")

product = get_product_by_id(999)
print(f"ID=999 的商品：{product}")  # None

phones = get_products_by_category("手机")
print(f"\n手机分类共 {len(phones)} 个商品：")
for p in phones:
    print(f"  - {p['name']}（¥{p['price']}）")

new_items = get_new_products()
print(f"\n新品共 {len(new_items)} 个：")
for p in new_items:
    print(f"  - {p['name']}（¥{p['price']}）")

cheap = get_products_by_price_range(0, 2000)
print(f"\n¥2000 以下的商品共 {len(cheap)} 个：")
for p in cheap:
    print(f"  - {p['name']}（¥{p['price']}）")

print()


# ========================================
# 第三步：商品搜索函数
# ========================================

def search_products(keyword):
    """
    搜索商品（模糊匹配名称和描述）

    参数：
        keyword: 搜索关键词

    返回：
        名称或描述中包含关键词的商品列表
    """
    keyword_lower = keyword.lower()
    results = []
    for p in products:
        name_match = keyword_lower in p["name"].lower()
        desc_match = keyword_lower in p["description"].lower()
        if name_match or desc_match:
            results.append(p)
    return results


def highlight_keyword(text, keyword):
    """
    在文本中高亮关键词（用 【】 包裹）

    参数：
        text: 原始文本
        keyword: 要高亮的关键词

    返回：
        高亮后的文本
    """
    result = text
    keyword_lower = keyword.lower()
    text_lower = text.lower()

    start = text_lower.find(keyword_lower)
    if start != -1:
        end = start + len(keyword)
        result = text[:start] + "【" + text[start:end] + "】" + text[end:]

    return result


# 测试搜索函数
print("【商品搜索】")
print("-" * 60)

search_keyword = "Pro"
results = search_products(search_keyword)
print(f"搜索 '{search_keyword}'，找到 {len(results)} 个结果：")
for p in results:
    highlighted_name = highlight_keyword(p["name"], search_keyword)
    print(f"  - {highlighted_name}（¥{p['price']}）")

print()

search_keyword = "芯片"
results = search_products(search_keyword)
print(f"搜索 '{search_keyword}'，找到 {len(results)} 个结果：")
for p in results:
    print(f"  - {p['name']}：{highlight_keyword(p['description'], search_keyword)}")

print()

search_keyword = "不存在的商品xyz"
results = search_products(search_keyword)
print(f"搜索 '{search_keyword}'，找到 {len(results)} 个结果")

print()


# ========================================
# 第四步：分页函数
# ========================================

def paginate(data, page=1, page_size=5):
    """
    对数据进行分页

    参数：
        data: 要分页的数据列表
        page: 页码（从 1 开始）
        page_size: 每页数量（默认 5）

    返回：
        分页结果字典，包含总数、页码、每页数量、数据、总页数
    """
    total = len(data)
    total_pages = (total + page_size - 1) // page_size  # 向上取整

    # 页码边界处理
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages

    start = (page - 1) * page_size
    end = start + page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": data[start:end]
    }


def print_pagination(result):
    """美观地打印分页结果"""
    print(f"  总计：{result['total']} 条")
    print(f"  页码：第 {result['page']}/{result['total_pages']} 页")
    print(f"  本页：{len(result['items'])} 条")
    for item in result["items"]:
        print(f"    - {item['name']}（¥{item['price']}）")


# 测试分页函数
print("【分页功能】")
print("-" * 60)

print("\n全部商品，第 1 页（每页 5 条）：")
page1 = paginate(products, page=1, page_size=5)
print_pagination(page1)

print("\n全部商品，第 2 页：")
page2 = paginate(products, page=2, page_size=5)
print_pagination(page2)

print("\n全部商品，第 3 页：")
page3 = paginate(products, page=3, page_size=5)
print_pagination(page3)

# 分类 + 分页组合
print("\n手机分类，第 1 页（每页 2 条）：")
phones = get_products_by_category("手机")
phones_page = paginate(phones, page=1, page_size=2)
print_pagination(phones_page)

# 边界测试：页码超出范围
print("\n页码超出范围测试：")
overflow = paginate(products, page=100, page_size=5)
print(f"  请求第 100 页，实际返回第 {overflow['page']} 页")

print()


# ========================================
# 第五步：用户登录验证函数
# ========================================

def login(username, password):
    """
    验证用户登录

    参数：
        username: 用户名
        password: 密码

    返回：
        登录结果字典，包含 success、message、user
    """
    # 检查用户名和密码是否为空
    if not username:
        return {"success": False, "message": "请输入用户名", "user": None}
    if not password:
        return {"success": False, "message": "请输入密码", "user": None}

    # 查找用户
    for user in users:
        if user["username"] == username:
            if user["password"] == password:
                # 登录成功，返回用户信息（不包含密码）
                safe_user = {
                    "id": user["id"],
                    "username": user["username"],
                    "nickname": user["nickname"],
                    "role": user["role"]
                }
                return {"success": True, "message": "登录成功", "user": safe_user}
            else:
                return {"success": False, "message": "密码错误", "user": None}

    return {"success": False, "message": "用户不存在", "user": None}


# 测试登录函数
print("【用户登录】")
print("-" * 60)

test_cases = [
    ("admin", "admin123", "正确账号密码"),
    ("admin", "wrong", "密码错误"),
    ("nobody", "123456", "用户不存在"),
    ("", "123456", "用户名为空"),
    ("admin", "", "密码为空"),
]

for username, password, desc in test_cases:
    result = login(username, password)
    status = "✅ 通过" if result["success"] else "❌ 失败"
    print(f"  {desc}：{status} - {result['message']}")

print()


# ========================================
# 第六步：购物车函数
# ========================================

# 购物车数据（内存中维护，程序结束后清空）
cart = []


def add_to_cart(product_id, quantity=1):
    """
    将商品添加到购物车

    参数：
        product_id: 商品 ID
        quantity: 数量（默认 1）

    返回：
        操作结果字典
    """
    product = get_product_by_id(product_id)
    if product is None:
        return {"success": False, "message": f"商品 ID={product_id} 不存在"}

    if product["stock"] < quantity:
        return {"success": False, "message": f"{product['name']} 库存不足（剩余 {product['stock']}）"}

    # 检查购物车中是否已有该商品
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["price"] * item["quantity"]
            return {"success": True, "message": f"{product['name']} 数量更新为 {item['quantity']}"}

    # 新商品，加入购物车
    cart.append({
        "product_id": product_id,
        "name": product["name"],
        "price": product["price"],
        "quantity": quantity,
        "subtotal": product["price"] * quantity
    })
    return {"success": True, "message": f"{product['name']} 已加入购物车"}


def remove_from_cart(product_id):
    """
    从购物车中移除商品

    参数：
        product_id: 商品 ID

    返回：
        操作结果字典
    """
    for i, item in enumerate(cart):
        if item["product_id"] == product_id:
            removed = cart.pop(i)
            return {"success": True, "message": f"{removed['name']} 已从购物车移除"}
    return {"success": False, "message": f"购物车中没有 ID={product_id} 的商品"}


def update_cart_quantity(product_id, quantity):
    """
    修改购物车中商品的数量

    参数：
        product_id: 商品 ID
        quantity: 新数量（设为 0 则删除）

    返回：
        操作结果字典
    """
    if quantity <= 0:
        return remove_from_cart(product_id)

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] = quantity
            item["subtotal"] = item["price"] * quantity
            return {"success": True, "message": f"{item['name']} 数量更新为 {quantity}"}

    return {"success": False, "message": f"购物车中没有 ID={product_id} 的商品"}


def get_cart_summary():
    """
    获取购物车摘要

    返回：
        包含商品列表、总数量、总价格的字典
    """
    total_items = 0
    total_price = 0
    for item in cart:
        total_items += item["quantity"]
        total_price += item["subtotal"]

    return {
        "items": cart,
        "total_items": total_items,
        "total_price": total_price,
        "item_count": len(cart)
    }


def clear_cart():
    """清空购物车"""
    cart.clear()
    return {"success": True, "message": "购物车已清空"}


def print_cart():
    """美观地打印购物车内容"""
    summary = get_cart_summary()
    if summary["item_count"] == 0:
        print("  购物车是空的")
        return

    for item in summary["items"]:
        print(f"  - {item['name']}  ¥{item['price']} × {item['quantity']} = ¥{item['subtotal']}")
    print(f"  {'—' * 40}")
    print(f"  共 {summary['total_items']} 件，合计 ¥{summary['total_price']}")


# 测试购物车函数
print("【购物车功能】")
print("-" * 60)

print("\n1. 添加商品到购物车：")
result = add_to_cart(1, 1)   # iPhone 15 Pro × 1
print(f"  {result['message']}")
result = add_to_cart(5, 2)   # MacBook Pro 14 × 2
print(f"  {result['message']}")
result = add_to_cart(11, 1)  # AirPods Pro 2 × 1
print(f"  {result['message']}")

print("\n2. 当前购物车：")
print_cart()

print("\n3. 再次添加同一商品（数量应该累加）：")
result = add_to_cart(1, 2)
print(f"  {result['message']}")

print("\n4. 修改商品数量：")
result = update_cart_quantity(5, 1)
print(f"  {result['message']}")

print("\n5. 删除一个商品：")
result = remove_from_cart(11)
print(f"  {result['message']}")

print("\n6. 最终购物车：")
print_cart()

print("\n7. 测试异常情况：")
result = add_to_cart(999, 1)
print(f"  添加不存在的商品：{result['message']}")

result = add_to_cart(1, 99999)
print(f"  库存不足时添加：{result['message']}")

print()


# ========================================
# 第七步：用列表推导式重写部分函数
# ========================================

print("【列表推导式 vs 普通写法对比】")
print("-" * 60)

# 对比 1：获取所有商品名
# 普通写法
names_normal = []
for p in products:
    names_normal.append(p["name"])

# 列表推导式
names_short = [p["name"] for p in products]

print(f"\n普通写法：{names_normal}")
print(f"列表推导式：{names_short}")
print(f"结果相同：{names_normal == names_short}")

# 对比 2：筛选手机
# 普通写法
phones_normal = []
for p in products:
    if p["category"] == "手机":
        phones_normal.append(p["name"])

# 列表推导式
phones_short = [p["name"] for p in products if p["category"] == "手机"]

print(f"\n手机（普通写法）：{phones_normal}")
print(f"手机（列表推导式）：{phones_short}")
print(f"结果相同：{phones_normal == phones_short}")

# 对比 3：格式化输出
summaries = [f"{p['name']}(¥{p['price']})" for p in products if p["price"] > 8000]
print(f"\n价格超过 ¥8000 的商品：{summaries}")

print()


# ========================================
# 总结统计
# ========================================
print("=" * 60)
print("本次编写了以下函数：")
print("=" * 60)
functions = [
    ("load_json(filename)", "加载 JSON 数据文件"),
    ("get_product_by_id(product_id)", "根据 ID 查询商品"),
    ("get_products_by_category(category)", "按分类筛选商品"),
    ("get_new_products()", "获取所有新品"),
    ("get_products_by_price_range(min, max)", "按价格区间筛选"),
    ("search_products(keyword)", "模糊搜索商品"),
    ("highlight_keyword(text, keyword)", "关键词高亮"),
    ("paginate(data, page, page_size)", "数据分页"),
    ("print_pagination(result)", "打印分页结果"),
    ("login(username, password)", "用户登录验证"),
    ("add_to_cart(product_id, quantity)", "添加到购物车"),
    ("remove_from_cart(product_id)", "从购物车移除"),
    ("update_cart_quantity(product_id, qty)", "修改购物车数量"),
    ("get_cart_summary()", "获取购物车摘要"),
    ("clear_cart()", "清空购物车"),
    ("print_cart()", "打印购物车"),
]

for func_name, desc in functions:
    print(f"  {func_name:<45} # {desc}")

print(f"\n共 {len(functions)} 个函数，覆盖了商品查询、搜索、分页、用户登录、购物车五大模块。")
