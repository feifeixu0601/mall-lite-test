"""
MallLite 电商系统 - 订单管理与数据统计
功能：订单创建、查询、取消、数据统计分析
"""

import json
import os
from datetime import datetime

# ========================================
# 加载数据
# ========================================
data_dir = "data"

def load_json(filename):
    """加载 JSON 数据文件"""
    filepath = os.path.join(data_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

products = load_json("products.json")
users = load_json("users.json")

# 复用上一篇的函数
def get_product_by_id(product_id):
    """根据 ID 查询商品"""
    for p in products:
        if p["id"] == product_id:
            return p
    return None

print(f"加载完成：{len(products)} 个商品，{len(users)} 个用户")
print("=" * 60)


# ========================================
# 第一部分：订单管理
# ========================================

# 订单列表（内存中维护）
orders = []
# 订单号计数器
order_counter = 0


def generate_order_no():
    """
    生成订单号：ORD + 日期 + 6 位序号
    例如：ORD20240115-000001
    """
    global order_counter
    order_counter += 1
    date_str = datetime.now().strftime("%Y%m%d")
    seq = str(order_counter).zfill(6)
    return f"ORD{date_str}-{seq}"


def create_order(user_id, cart_items):
    """
    从购物车创建订单

    参数：
        user_id: 用户 ID
        cart_items: 购物车商品列表，每个元素格式：
                    {"product_id": 1, "quantity": 2}

    返回：
        创建结果字典，包含 success、message、order
    """
    # 验证购物车是否为空
    if not cart_items:
        return {"success": False, "message": "购物车为空，无法创建订单", "order": None}

    # 构建订单商品明细
    order_items = []
    total_price = 0

    for cart_item in cart_items:
        product_id = cart_item["product_id"]
        quantity = cart_item["quantity"]

        # 查找商品
        product = get_product_by_id(product_id)
        if product is None:
            return {"success": False, "message": f"商品 ID={product_id} 不存在", "order": None}

        # 检查库存
        if product["stock"] < quantity:
            return {
                "success": False,
                "message": f"{product['name']} 库存不足（需要 {quantity}，剩余 {product['stock']}）",
                "order": None
            }

        # 构建订单项
        subtotal = product["price"] * quantity
        order_items.append({
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "subtotal": subtotal
        })
        total_price += subtotal

    # 扣减库存
    for cart_item in cart_items:
        product = get_product_by_id(cart_item["product_id"])
        product["stock"] -= cart_item["quantity"]

    # 创建订单
    order_no = generate_order_no()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order = {
        "order_no": order_no,
        "user_id": user_id,
        "items": order_items,
        "total_price": total_price,
        "item_count": len(order_items),
        "total_quantity": sum(item["quantity"] for item in order_items),
        "status": "待支付",
        "created_at": now,
        "updated_at": now
    }

    orders.append(order)

    return {"success": True, "message": f"订单 {order_no} 创建成功", "order": order}


def get_order_list(user_id=None, status=None):
    """
    获取订单列表，支持按用户和状态筛选

    参数：
        user_id: 用户 ID（可选，不传则返回所有订单）
        status: 订单状态（可选，如 "待支付"、"已取消"）

    返回：
        符合条件的订单列表
    """
    result = orders

    if user_id is not None:
        result = [o for o in result if o["user_id"] == user_id]

    if status is not None:
        result = [o for o in result if o["status"] == status]

    return result


def get_order_by_no(order_no):
    """
    根据订单号查询订单

    参数：
        order_no: 订单号

    返回：
        找到返回订单字典，找不到返回 None
    """
    for order in orders:
        if order["order_no"] == order_no:
            return order
    return None


def cancel_order(order_no):
    """
    取消订单（恢复库存）

    参数：
        order_no: 订单号

    返回：
        操作结果字典
    """
    order = get_order_by_no(order_no)
    if order is None:
        return {"success": False, "message": f"订单 {order_no} 不存在"}

    if order["status"] == "已取消":
        return {"success": False, "message": f"订单 {order_no} 已经是取消状态"}

    if order["status"] == "已完成":
        return {"success": False, "message": f"订单 {order_no} 已完成，无法取消"}

    # 恢复库存
    for item in order["items"]:
        product = get_product_by_id(item["product_id"])
        if product:
            product["stock"] += item["quantity"]

    order["status"] = "已取消"
    order["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {"success": True, "message": f"订单 {order_no} 已取消，库存已恢复"}


def pay_order(order_no):
    """
    支付订单

    参数：
        order_no: 订单号

    返回：
        操作结果字典
    """
    order = get_order_by_no(order_no)
    if order is None:
        return {"success": False, "message": f"订单 {order_no} 不存在"}

    if order["status"] != "待支付":
        return {"success": False, "message": f"订单 {order_no} 状态为 {order['status']}，无法支付"}

    order["status"] = "已支付"
    order["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {"success": True, "message": f"订单 {order_no} 支付成功，金额 ¥{order['total_price']}"}


def print_order(order):
    """美观地打印订单详情"""
    print(f"  订单号：{order['order_no']}")
    print(f"  状态：{order['status']}")
    print(f"  下单时间：{order['created_at']}")
    print(f"  商品明细：")
    for item in order["items"]:
        print(f"    - {item['name']}  ¥{item['price']} × {item['quantity']} = ¥{item['subtotal']}")
    print(f"  合计：{order['total_quantity']} 件，¥{order['total_price']}")


# ========================================
# 测试订单管理
# ========================================
print("\n【订单管理功能】")
print("-" * 60)

# 模拟登录用户
current_user = users[1]  # testuser

print(f"\n当前用户：{current_user['nickname']}（ID={current_user['id']}）")

# 订单 1：正常下单
print("\n1. 创建订单 1（正常下单）：")
cart1 = [
    {"product_id": 1, "quantity": 1},   # iPhone 15 Pro × 1
    {"product_id": 11, "quantity": 2},   # AirPods Pro 2 × 2
]
result = create_order(current_user["id"], cart1)
print(f"  {result['message']}")
if result["success"]:
    print_order(result["order"])
    order1_no = result["order"]["order_no"]

# 订单 2：另一笔订单
print("\n2. 创建订单 2（购买笔记本）：")
cart2 = [
    {"product_id": 5, "quantity": 1},   # MacBook Pro 14 × 1
]
result = create_order(current_user["id"], cart2)
print(f"  {result['message']}")
if result["success"]:
    print_order(result["order"])
    order2_no = result["order"]["order_no"]

# 订单 3：库存不足
print("\n3. 测试库存不足：")
cart3 = [{"product_id": 5, "quantity": 999}]
result = create_order(current_user["id"], cart3)
print(f"  {result['message']}")

# 订单 4：空购物车
print("\n4. 测试空购物车下单：")
result = create_order(current_user["id"], [])
print(f"  {result['message']}")

# 支付订单 1
print("\n5. 支付订单 1：")
result = pay_order(order1_no)
print(f"  {result['message']}")

# 取消订单 2
print("\n6. 取消订单 2：")
result = cancel_order(order2_no)
print(f"  {result['message']}")

# 查看当前用户所有订单
print(f"\n7. {current_user['nickname']} 的所有订单：")
user_orders = get_order_list(user_id=current_user["id"])
for order in user_orders:
    print(f"  - {order['order_no']} | {order['status']} | ¥{order['total_price']}")

# 按状态筛选
print(f"\n8. 筛选已支付的订单：")
paid_orders = get_order_list(status="已支付")
for order in paid_orders:
    print(f"  - {order['order_no']} | ¥{order['total_price']}")

print()


# ========================================
# 第二部分：数据统计分析
# ========================================
print("【数据统计分析】")
print("=" * 60)


# ========================================
# 统计 1：各分类商品数量和平均价格
# ========================================
print("\n统计 1：各分类商品统计")
print("-" * 60)

def analyze_categories(products):
    """
    统计各分类的商品数量、平均价格、最高价、最低价

    参数：
        products: 商品列表

    返回：
        各分类的统计数据字典
    """
    stats = {}

    for p in products:
        cat = p["category"]
        if cat not in stats:
            stats[cat] = {
                "count": 0,
                "total_price": 0,
                "prices": [],
                "names": []
            }
        stats[cat]["count"] += 1
        stats[cat]["total_price"] += p["price"]
        stats[cat]["prices"].append(p["price"])
        stats[cat]["names"].append(p["name"])

    # 计算统计值
    for cat, data in stats.items():
        data["avg_price"] = data["total_price"] / data["count"]
        data["min_price"] = min(data["prices"])
        data["max_price"] = max(data["prices"])
        # 删除临时字段，只保留统计数据
        del data["prices"]

    return stats

category_stats = analyze_categories(products)

# 用格式化对齐输出
print(f"  {'分类':<8} {'数量':>4} {'平均价':>8} {'最低价':>8} {'最高价':>8}")
print(f"  {'—' * 40}")
for cat, data in category_stats.items():
    print(f"  {cat:<8} {data['count']:>4} {data['avg_price']:>8.0f} {data['min_price']:>8} {data['max_price']:>8}")


# ========================================
# 统计 2：价格区间分布
# ========================================
print(f"\n统计 2：价格区间分布")
print("-" * 60)

def analyze_price_distribution(products):
    """
    统计商品在各价格区间的分布

    参数：
        products: 商品列表

    返回：
        各区间的商品数量和占比
    """
    ranges = [
        ("¥0-500", 0, 500),
        ("¥500-2000", 500, 2000),
        ("¥2000-5000", 2000, 5000),
        ("¥5000-10000", 5000, 10000),
        ("¥10000+", 10000, float("inf")),
    ]

    total = len(products)
    distribution = []

    for label, low, high in ranges:
        count = len([p for p in products if low <= p["price"] < high])
        percentage = count / total * 100 if total > 0 else 0
        distribution.append({
            "range": label,
            "count": count,
            "percentage": percentage,
            "names": [p["name"] for p in products if low <= p["price"] < high]
        })

    return distribution

distribution = analyze_price_distribution(products)

for item in distribution:
    bar = "█" * int(item["percentage"] / 5)  # 每 5% 一个方块
    print(f"  {item['range']:<12} {item['count']:>2} 个 ({item['percentage']:>5.1f}%) {bar}")


# ========================================
# 统计 3：库存预警
# ========================================
print(f"\n统计 3：库存预警（低于 80 件）")
print("-" * 60)

def get_stock_alerts(products, threshold=80):
    """
    获取库存预警商品

    参数：
        products: 商品列表
        threshold: 库存阈值

    返回：
        低于阈值的商品列表，按库存从低到高排序
    """
    alerts = [p for p in products if p["stock"] < threshold]
    return sorted(alerts, key=lambda p: p["stock"])

alerts = get_stock_alerts(products, threshold=80)

if alerts:
    for p in alerts:
        level = "🔴 紧急" if p["stock"] < 50 else "🟡 预警"
        print(f"  {level} {p['name']:<20} 仅剩 {p['stock']} 件")
else:
    print("  所有商品库存充足")


# ========================================
# 统计 4：新品与非新品对比
# ========================================
print(f"\n统计 4：新品 vs 非新品")
print("-" * 60)

def compare_new_vs_old(products):
    """
    对比新品和非新品的数量、平均价格、平均评分

    返回：
        包含新品和非新品统计数据的字典
    """
    new_items = [p for p in products if p["is_new"]]
    old_items = [p for p in products if not p["is_new"]]

    def calc_stats(items, label):
        if not items:
            return {"label": label, "count": 0, "avg_price": 0, "avg_rating": 0}
        return {
            "label": label,
            "count": len(items),
            "avg_price": sum(p["price"] for p in items) / len(items),
            "avg_rating": sum(p["rating"] for p in items) / len(items),
        }

    return calc_stats(new_items, "新品"), calc_stats(old_items, "非新品")

new_stats, old_stats = compare_new_vs_old(products)

print(f"  {'类型':<8} {'数量':>4} {'平均价格':>10} {'平均评分':>8}")
print(f"  {'—' * 36}")
for stats in [new_stats, old_stats]:
    print(f"  {stats['label']:<8} {stats['count']:>4} {stats['avg_price']:>10.0f} {stats['avg_rating']:>8.1f}")


# ========================================
# 统计 5：订单统计（如果有订单数据）
# ========================================
print(f"\n统计 5：订单统计")
print("-" * 60)

def analyze_orders(order_list):
    """
    统计订单数据

    参数：
        order_list: 订单列表

    返回：
        订单统计数据字典
    """
    if not order_list:
        return {
            "total_orders": 0,
            "total_revenue": 0,
            "avg_order_price": 0,
            "status_distribution": {},
            "top_products": []
        }

    # 按状态统计
    status_count = {}
    for order in order_list:
        status = order["status"]
        if status not in status_count:
            status_count[status] = 0
        status_count[status] += 1

    # 计算总收入（只统计已支付的订单）
    paid_orders = [o for o in order_list if o["status"] == "已支付"]
    total_revenue = sum(o["total_price"] for o in paid_orders)

    # 统计商品销量
    product_sales = {}
    for order in order_list:
        if order["status"] != "已取消":
            for item in order["items"]:
                name = item["name"]
                if name not in product_sales:
                    product_sales[name] = 0
                product_sales[name] += item["quantity"]

    # 按销量排序取前 5
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_orders": len(order_list),
        "total_revenue": total_revenue,
        "avg_order_price": total_revenue / len(paid_orders) if paid_orders else 0,
        "status_distribution": status_count,
        "top_products": top_products
    }

order_stats = analyze_orders(orders)

print(f"  总订单数：{order_stats['total_orders']}")
print(f"  已支付收入：¥{order_stats['total_revenue']}")
print(f"  平均客单价：¥{order_stats['avg_order_price']:.0f}")
print(f"  状态分布：")
for status, count in order_stats["status_distribution"].items():
    print(f"    {status}：{count} 笔")
if order_stats["top_products"]:
    print(f"  销量 Top 商品：")
    for name, qty in order_stats["top_products"]:
        print(f"    {name}：{qty} 件")


# ========================================
# 统计 6：用字典推导式做快速统计
# ========================================
print(f"\n统计 6：字典推导式快速统计")
print("-" * 60)

# 商品名 → 价格 映射
price_map = {p["name"]: p["price"] for p in products}
print(f"  商品价格映射（前 5 个）：")
for i, (name, price) in enumerate(price_map.items()):
    if i >= 5:
        break
    print(f"    {name} → ¥{price}")

# 各分类最低价商品
cheapest_by_category = {}
for p in products:
    cat = p["category"]
    if cat not in cheapest_by_category or p["price"] < cheapest_by_category[cat]["price"]:
        cheapest_by_category[cat] = p

print(f"\n  各分类最低价商品：")
for cat, p in cheapest_by_category.items():
    print(f"    {cat}：{p['name']}（¥{p['price']}）")


# ========================================
# 总结
# ========================================
print(f"\n{'=' * 60}")
print("本次编写了以下函数和统计模块：")
print("=" * 60)

functions = [
    ("generate_order_no()", "生成订单号"),
    ("create_order(user_id, cart_items)", "创建订单"),
    ("get_order_list(user_id, status)", "获取订单列表（支持筛选）"),
    ("get_order_by_no(order_no)", "根据订单号查询"),
    ("cancel_order(order_no)", "取消订单（恢复库存）"),
    ("pay_order(order_no)", "支付订单"),
    ("print_order(order)", "打印订单详情"),
    ("analyze_categories(products)", "各分类商品统计"),
    ("analyze_price_distribution(products)", "价格区间分布"),
    ("get_stock_alerts(products, threshold)", "库存预警"),
    ("compare_new_vs_old(products)", "新品 vs 非新品对比"),
    ("analyze_orders(order_list)", "订单统计"),
]

for func_name, desc in functions:
    print(f"  {func_name:<48} # {desc}")

print(f"\n数据结构使用统计：")
usage = [
    ("列表 list", "商品列表、订单列表、购物车、统计结果"),
    ("字典 dict", "商品信息、订单信息、配置、统计映射"),
    ("集合 set", "分类去重、权限对比"),
    ("元组 tuple", "函数多返回值、价格区间定义"),
    ("列表推导式", "筛选商品、提取字段、数据转换"),
    ("字典推导式", "价格映射、最低价统计"),
    ("嵌套结构", "订单包含商品列表，每个商品又是一个字典"),
]
for struct, usage_desc in usage:
    print(f"  {struct:<16} → {usage_desc}")