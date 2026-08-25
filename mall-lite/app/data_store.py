"""
MallLite DataStore - 改进版（集成日志）
在 P04 基础上改为面向对象模型，内部使用 Product / User / Order 等类
"""

import json
import os
import logging                                    # ← 新增
from pathlib import Path
from datetime import datetime

from app.models import User, Product, CartItem, Order

logger = logging.getLogger("malllite")            # ← 新增：获取 logger


class DataStore:
    """数据存储层"""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache = {}                          # ← 新增：缓存

        self._files = {
            "products": self.data_dir / "products.json",
            "categories": self.data_dir / "categories.json",
            "users": self.data_dir / "users.json",
            "orders": self.data_dir / "orders.json",
            "carts": self.data_dir / "carts.json",
        }

        # 初始化空文件
        for name, filepath in self._files.items():
            if not filepath.exists() and name in ["orders", "carts"]:
                self._write_json(filepath, [] if name == "orders" else {})

        self._order_counter = 0
        logger.info(f"DataStore 初始化完成，数据目录：{self.data_dir}")  # ← 新增

    # ====== 底层文件操作 ======

    def _read_json(self, filepath):
        filepath = Path(filepath)
        if not filepath.exists():
            logger.warning(f"文件不存在：{filepath}")                    # ← 新增
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.debug(f"读取文件成功：{filepath}（{len(data) if isinstance(data, list) else 'dict'}）")  # ← 新增
                return data
        except (json.JSONDecodeError, PermissionError) as e:
            logger.error(f"读取文件失败：{filepath}，{e}")               # ← 修改：原为 print
            return None

    def _write_json(self, filepath, data):
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"写入文件成功：{filepath}")                     # ← 新增
        except (PermissionError, TypeError) as e:
            logger.error(f"写入文件失败：{filepath}，{e}")                # ← 修改：原为 print

    # ====== 用户操作 ======

    def get_users(self):
        data = self._read_json(self._files["users"]) or []
        return [User.from_dict(u) for u in data]

    def get_user_by_username(self, username):
        for user in self.get_users():
            if user.username == username:
                return user
        return None

    def verify_login(self, username, password):
        if not username:
            logger.warning("登录失败：用户名为空")                       # ← 新增
            return {"success": False, "message": "请输入用户名", "user": None}
        if not password:
            logger.warning("登录失败：密码为空")                         # ← 新增
            return {"success": False, "message": "请输入密码", "user": None}

        user = self.get_user_by_username(username)
        if user is None:
            logger.warning(f"登录失败：用户 {username} 不存在")          # ← 新增
            return {"success": False, "message": "用户不存在", "user": None}
        if not user.check_password(password):
            logger.warning(f"登录失败：用户 {username} 密码错误")        # ← 新增
            return {"success": False, "message": "密码错误", "user": None}

        logger.info(f"用户 {username} 登录成功")                         # ← 新增
        return {"success": True, "message": "登录成功", "user": user.to_dict()}

    # ====== 商品操作 ======

    def get_products(self):
        data = self._read_json(self._files["products"]) or []
        return [Product.from_dict(p) for p in data]

    def get_product_by_id(self, product_id):
        for p in self.get_products():
            if p.id == product_id:
                return p
        return None

    def search_products(self, keyword):
        keyword_lower = keyword.lower()
        return [
            p for p in self.get_products()
            if keyword_lower in p.name.lower()
            or keyword_lower in p.description.lower()
        ]

    def get_products_by_category(self, category):
        return [p for p in self.get_products() if p.category == category]

    # ====== 分类操作 ======

    def get_categories(self):
        return self._read_json(self._files["categories"]) or []

    # ====== 购物车操作 ======

    def get_cart(self, user_id):
        carts = self._read_json(self._files["carts"]) or {}
        cart_data = carts.get(str(user_id), [])
        return [CartItem(**item) for item in cart_data]

    def add_to_cart(self, user_id, product_id, quantity=1):
        product = self.get_product_by_id(product_id)
        if product is None:
            logger.warning(f"添加购物车失败：商品 ID={product_id} 不存在")      # ← 新增
            return {"success": False, "message": "商品不存在"}
        if not product.is_in_stock(quantity):
            logger.warning(f"添加购物车失败：{product.name} 库存不足（需要 {quantity}，剩余 {product.stock}）")  # ← 新增
            return {"success": False, "message": f"{product.name} 库存不足"}

        carts = self._read_json(self._files["carts"]) or {}
        user_cart = carts.get(str(user_id), [])

        for item in user_cart:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                carts[str(user_id)] = user_cart
                self._write_json(self._files["carts"], carts)
                logger.info(f"用户 {user_id} 更新购物车：{product.name} 数量更新为 {item['quantity']}")  # ← 新增
                return {"success": True, "message": f"{product.name} 数量更新为 {item['quantity']}"}

        user_cart.append({
            "product_id": product_id,
            "name": product.name,
            "price": product.price,
            "quantity": quantity,
        })
        carts[str(user_id)] = user_cart
        self._write_json(self._files["carts"], carts)
        logger.info(f"用户 {user_id} 添加购物车：{product.name} × {quantity}")   # ← 新增
        return {"success": True, "message": f"{product.name} 已加入购物车"}

    def update_cart_quantity(self, user_id, product_id, quantity):
        carts = self._read_json(self._files["carts"]) or {}
        user_cart = carts.get(str(user_id), [])

        for item in user_cart:
            if item["product_id"] == product_id:
                if quantity <= 0:
                    user_cart.remove(item)
                else:
                    item["quantity"] = quantity
                carts[str(user_id)] = user_cart
                self._write_json(self._files["carts"], carts)
                logger.info(f"用户 {user_id} 更新购物车：商品 {product_id} 数量设为 {quantity}")  # ← 新增
                return {"success": True, "message": "购物车已更新"}

        logger.warning(f"用户 {user_id} 更新购物车失败：商品 {product_id} 不在购物车中")           # ← 新增
        return {"success": False, "message": "商品不在购物车中"}

    def remove_from_cart(self, user_id, product_id):
        return self.update_cart_quantity(user_id, product_id, 0)

    def clear_cart(self, user_id):
        carts = self._read_json(self._files["carts"]) or {}
        carts[str(user_id)] = []
        self._write_json(self._files["carts"], carts)
        logger.info(f"用户 {user_id} 购物车已清空")                        # ← 新增

    def get_cart_total(self, user_id):
        cart = self.get_cart(user_id)
        total = sum(item.price * item.quantity for item in cart)
        count = sum(item.quantity for item in cart)
        return {"total_price": total, "total_quantity": count, "item_count": len(cart)}

    # ====== 订单操作 ======

    def get_orders(self):
        data = self._read_json(self._files["orders"]) or []
        return data

    def get_order_by_no(self, order_no):
        for order in self.get_orders():
            if order["order_no"] == order_no:
                return order
        return None

    def create_order(self, user_id, cart_items):
        if not cart_items:
            logger.warning(f"创建订单失败：用户 {user_id} 购物车为空")       # ← 新增
            return {"success": False, "message": "购物车为空", "order": None}

        self._order_counter += 1
        date_str = datetime.now().strftime("%Y%m%d")
        order_no = f"ORD{date_str}-{str(self._order_counter).zfill(6)}"

        order_items = []
        total_price = 0

        for item in cart_items:
            product = self.get_product_by_id(item.product_id)
            if product is None:
                logger.error(f"创建订单失败：商品 ID={item.product_id} 不存在")  # ← 新增
                return {"success": False, "message": f"商品不存在", "order": None}
            if not product.is_in_stock(item.quantity):
                logger.warning(f"创建订单失败：{product.name} 库存不足")         # ← 新增
                return {"success": False, "message": f"{product.name} 库存不足", "order": None}

            subtotal = product.price * item.quantity
            order_items.append({
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "subtotal": subtotal,
            })
            total_price += subtotal
            product.reduce_stock(item.quantity)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order = {
            "order_no": order_no,
            "user_id": user_id,
            "items": order_items,
            "total_price": total_price,
            "total_quantity": sum(i["quantity"] for i in order_items),
            "item_count": len(order_items),
            "status": "待支付",
            "created_at": now,
            "updated_at": now,
        }

        orders = self.get_orders()
        orders.append(order)
        self._write_json(self._files["orders"], orders)

        # 保存更新后的库存
        self._write_json(self._files["products"], [p.to_dict() for p in self.get_products()])

        # 清空购物车
        self.clear_cart(user_id)

        logger.info(f"订单创建成功：{order_no}，用户 {user_id}，金额 ¥{total_price}")  # ← 新增
        return {"success": True, "message": f"订单 {order_no} 创建成功", "order": order}

    def update_order_status(self, order_no, new_status):
        orders = self.get_orders()
        for order in orders:
            if order["order_no"] == order_no:
                old_status = order["status"]                                      # ← 新增：记录旧状态
                order["status"] = new_status
                order["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._write_json(self._files["orders"], orders)
                logger.info(f"订单 {order_no} 状态变更：{old_status} → {new_status}")  # ← 新增
                return True

        logger.warning(f"更新订单状态失败：订单 {order_no} 不存在")              # ← 新增
        return False

    def get_orders_by_user(self, user_id):
        return [o for o in self.get_orders() if o["user_id"] == user_id]