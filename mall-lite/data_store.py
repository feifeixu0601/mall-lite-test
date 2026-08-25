"""
MallLite 电商系统 - DataStore 数据存储层
功能：统一管理所有数据的读写、缓存、备份
用法：
    store = DataStore()
    products = store.get_products()
    store.add_order(order)
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path


class DataStore:
    """
    MallLite 数据存储层

    用 JSON 文件模拟数据库，提供统一的数据读写接口。
    所有数据操作都通过这个类进行，不再直接读写文件。
    """

    def __init__(self, data_dir="data"):
        """
        初始化数据存储

        参数：
            data_dir: 数据文件存放目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存（加载过的数据缓存起来，避免重复读文件）
        self._cache = {}

        # 数据文件路径映射
        self._files = {
            "products": self.data_dir / "products.json",
            "categories": self.data_dir / "categories.json",
            "users": self.data_dir / "users.json",
            "orders": self.data_dir / "orders.json",
            "carts": self.data_dir / "carts.json",
            "config": self.data_dir / "config.json",
        }

        # 初始化数据文件（不存在则创建空文件）
        self._init_files()

        print(f"DataStore 初始化完成，数据目录：{self.data_dir}")

    # ============================
    # 内部方法（不对外暴露）
    # ============================

    def _init_files(self):
        """初始化数据文件，不存在则创建默认值"""
        defaults = {
            "orders": [],
            "carts": {},
            "config": {
                "site_name": "MallLite",
                "version": "1.0.0",
                "page_size": 10
            }
        }

        for name, filepath in self._files.items():
            if not filepath.exists() and name in defaults:
                self._write_json(filepath, defaults[name])
                print(f"  初始化文件：{filepath.name}")

    def _read_json(self, filepath):
        """
        读取 JSON 文件

        参数：
            filepath: 文件路径（Path 对象或字符串）

        返回：
            解析后的 Python 对象，读取失败返回 None
        """
        filepath = Path(filepath)

        if not filepath.exists():
            print(f"文件不存在：{filepath}")
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误：{filepath}，错误：{e}")
            return None
        except PermissionError:
            print(f"没有权限读取文件：{filepath}")
            return None

    def _write_json(self, filepath, data):
        """
        写入 JSON 文件

        参数：
            filepath: 文件路径
            data: 要写入的数据
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except PermissionError:
            print(f"没有权限写入文件：{filepath}")
            return False
        except TypeError as e:
            print(f"数据序列化错误：{e}")
            return False

    def _get_data(self, name):
        """
        获取数据（优先从缓存读取）

        参数：
            name: 数据名称（如 "products"、"users"）

        返回：
            数据对象
        """
        # 优先从缓存读取
        if name in self._cache:
            return self._cache[name]

        # 缓存没有，从文件读取
        filepath = self._files.get(name)
        if filepath is None:
            print(f"未知的数据类型：{name}")
            return None

        data = self._read_json(filepath)
        if data is not None:
            self._cache[name] = data

        return data

    def _save_data(self, name, data):
        """
        保存数据（同时更新缓存和文件）

        参数：
            name: 数据名称
            data: 要保存的数据
        """
        self._cache[name] = data
        filepath = self._files.get(name)
        if filepath:
            self._write_json(filepath, data)

    # ============================
    # 商品相关方法
    # ============================

    def get_products(self):
        """获取所有商品列表"""
        return self._get_data("products") or []

    def get_product_by_id(self, product_id):
        """
        根据 ID 查询商品

        参数：
            product_id: 商品 ID

        返回：
            商品字典或 None
        """
        products = self.get_products()
        for p in products:
            if p["id"] == product_id:
                return p
        return None

    def search_products(self, keyword):
        """
        搜索商品（匹配名称和描述）

        参数：
            keyword: 搜索关键词

        返回：
            匹配的商品列表
        """
        keyword_lower = keyword.lower()
        return [
            p for p in self.get_products()
            if keyword_lower in p["name"].lower()
            or keyword_lower in p.get("description", "").lower()
        ]

    def get_products_by_category(self, category):
        """按分类筛选商品"""
        return [p for p in self.get_products() if p["category"] == category]

    def update_product_stock(self, product_id, quantity_change):
        """
        更新商品库存

        参数：
            product_id: 商品 ID
            quantity_change: 库存变化量（正数增加，负数减少）

        返回：
            更新成功返回 True，商品不存在返回 False
        """
        products = self.get_products()
        for p in products:
            if p["id"] == product_id:
                new_stock = p["stock"] + quantity_change
                if new_stock < 0:
                    print(f"库存不足：{p['name']} 当前库存 {p['stock']}，尝试减少 {abs(quantity_change)}")
                    return False
                p["stock"] = new_stock
                self._save_data("products", products)
                return True
        return False

    # ============================
    # 用户相关方法
    # ============================

    def get_users(self):
        """获取所有用户列表"""
        return self._get_data("users") or []

    def get_user_by_username(self, username):
        """根据用户名查询用户"""
        for user in self.get_users():
            if user["username"] == username:
                return user
        return None

    def verify_login(self, username, password):
        """
        验证登录

        返回：
            {"success": bool, "message": str, "user": dict or None}
        """
        if not username:
            return {"success": False, "message": "请输入用户名", "user": None}
        if not password:
            return {"success": False, "message": "请输入密码", "user": None}

        user = self.get_user_by_username(username)
        if user is None:
            return {"success": False, "message": "用户不存在", "user": None}
        if user["password"] != password:
            return {"success": False, "message": "密码错误", "user": None}

        safe_user = {k: v for k, v in user.items() if k != "password"}
        return {"success": True, "message": "登录成功", "user": safe_user}

    # ============================
    # 分类相关方法
    # ============================

    def get_categories(self):
        """获取所有分类"""
        return self._get_data("categories") or []

    # ============================
    # 订单相关方法
    # ============================

    def get_orders(self):
        """获取所有订单"""
        return self._get_data("orders") or []

    def get_order_by_no(self, order_no):
        """根据订单号查询"""
        for order in self.get_orders():
            if order["order_no"] == order_no:
                return order
        return None

    def add_order(self, order):
        """
        添加订单

        参数：
            order: 订单字典

        返回：
            添加成功返回 True
        """
        orders = self.get_orders()
        orders.append(order)
        self._save_data("orders", orders)
        return True

    def update_order_status(self, order_no, new_status):
        """
        更新订单状态

        参数：
            order_no: 订单号
            new_status: 新状态

        返回：
            更新成功返回 True
        """
        orders = self.get_orders()
        for order in orders:
            if order["order_no"] == order_no:
                order["status"] = new_status
                order["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data("orders", orders)
                return True
        return False

    def get_orders_by_user(self, user_id):
        """获取某个用户的所有订单"""
        return [o for o in self.get_orders() if o["user_id"] == user_id]

    def get_orders_by_status(self, status):
        """按状态筛选订单"""
        return [o for o in self.get_orders() if o["status"] == status]

    # ============================
    # 购物车相关方法
    # ============================

    def get_cart(self, user_id):
        """获取用户的购物车"""
        carts = self._get_data("carts") or {}
        return carts.get(str(user_id), [])

    def add_to_cart(self, user_id, product_id, quantity=1):
        """
        添加商品到购物车

        返回：
            {"success": bool, "message": str}
        """
        product = self.get_product_by_id(product_id)
        if product is None:
            return {"success": False, "message": f"商品 ID={product_id} 不存在"}
        if product["stock"] < quantity:
            return {"success": False, "message": f"{product['name']} 库存不足"}

        carts = self._get_data("carts") or {}
        user_cart = carts.get(str(user_id), [])

        # 检查是否已在购物车中
        for item in user_cart:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                carts[str(user_id)] = user_cart
                self._save_data("carts", carts)
                return {"success": True, "message": f"{product['name']} 数量更新为 {item['quantity']}"}

        # 新商品
        user_cart.append({
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity
        })
        carts[str(user_id)] = user_cart
        self._save_data("carts", carts)
        return {"success": True, "message": f"{product['name']} 已加入购物车"}

    def clear_cart(self, user_id):
        """清空用户购物车"""
        carts = self._get_data("carts") or {}
        carts[str(user_id)] = []
        self._save_data("carts", carts)

    # ============================
    # 配置相关方法
    # ============================

    def get_config(self, key=None, default=None):
        """
        获取配置

        参数：
            key: 配置键名（不传则返回全部配置）
            default: 键不存在时的默认值

        返回：
            配置值或全部配置字典
        """
        config = self._get_data("config") or {}
        if key is None:
            return config
        return config.get(key, default)

    def set_config(self, key, value):
        """设置配置项"""
        config = self._get_data("config") or {}
        config[key] = value
        self._save_data("config", config)

    # ============================
    # 工具方法
    # ============================

    def clear_cache(self):
        """清空内存缓存"""
        self._cache.clear()
        print("缓存已清空")

    def backup(self, backup_dir="backup"):
        """
        备份所有数据文件

        参数：
            backup_dir: 备份目录

        返回：
            备份目录路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(backup_dir) / timestamp

        try:
            shutil.copytree(self.data_dir, backup_path)
            print(f"数据已备份到：{backup_path}")
            return str(backup_path)
        except Exception as e:
            print(f"备份失败：{e}")
            return None

    def restore(self, backup_path):
        """
        从备份恢复数据

        参数：
            backup_path: 备份目录路径
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            print(f"备份目录不存在：{backup_path}")
            return False

        try:
            # 清空当前数据
            shutil.rmtree(self.data_dir)
            # 复制备份数据
            shutil.copytree(backup_path, self.data_dir)
            # 清空缓存，强制重新加载
            self.clear_cache()
            print(f"数据已从 {backup_path} 恢复")
            return True
        except Exception as e:
            print(f"恢复失败：{e}")
            return False

    def get_stats(self):
        """获取数据统计信息"""
        products = self.get_products()
        users = self.get_users()
        orders = self.get_orders()
        categories = self.get_categories()

        return {
            "商品总数": len(products),
            "用户总数": len(users),
            "订单总数": len(orders),
            "分类总数": len(categories),
            "商品分类明细": {cat["name"]: len(self.get_products_by_category(cat["name"])) for cat in categories},
            "缓存数据项": list(self._cache.keys()),
            "数据目录": str(self.data_dir),
        }


# ========================================
# 测试 DataStore
# ========================================
if __name__ == "__main__":

    print("=" * 60)
    print("MallLite DataStore 测试")
    print("=" * 60)

    # 创建 DataStore 实例
    store = DataStore("data")

    # ============================================
    # 测试 1：商品操作
    # ============================================
    print("\n【测试 1：商品操作】")
    print("-" * 60)

    products = store.get_products()
    print(f"商品总数：{len(products)}")

    product = store.get_product_by_id(1)
    print(f"ID=1：{product['name']}（¥{product['price']}，库存 {product['stock']}）")

    results = store.search_products("Pro")
    print(f"搜索 'Pro'：{len(results)} 个结果")
    for p in results:
        print(f"  - {p['name']}")

    phones = store.get_products_by_category("手机")
    print(f"手机分类：{len(phones)} 个")

    # 更新库存
    old_stock = store.get_product_by_id(1)["stock"]
    store.update_product_stock(1, -2)  # 减少 2 件
    new_stock = store.get_product_by_id(1)["stock"]
    print(f"ID=1 库存变化：{old_stock} → {new_stock}（-2）")

    # ============================================
    # 测试 2：用户操作
    # ============================================
    print("\n【测试 2：用户登录验证】")
    print("-" * 60)

    test_logins = [
        ("admin", "admin123"),
        ("admin", "wrong"),
        ("nobody", "123"),
        ("", "123"),
    ]

    for username, password in test_logins:
        result = store.verify_login(username, password)
        status = "通过" if result["success"] else "失败"
        print(f"  {username or '(空)':<10} + {password:<10} → {status}：{result['message']}")

    # ============================================
    # 测试 3：购物车操作
    # ============================================
    print("\n【测试 3：购物车操作】")
    print("-" * 60)

    user_id = 2

    # 清空购物车
    store.clear_cart(user_id)

    # 添加商品
    result = store.add_to_cart(user_id, 1, 1)
    print(f"  {result['message']}")
    result = store.add_to_cart(user_id, 5, 2)
    print(f"  {result['message']}")
    result = store.add_to_cart(user_id, 1, 3)
    print(f"  {result['message']}")

    # 查看购物车
    cart = store.get_cart(user_id)
    print(f"\n  购物车（用户 {user_id}）：")
    for item in cart:
        print(f"    - {item['name']}  ¥{item['price']} × {item['quantity']}")

    # ============================================
    # 测试 4：订单操作
    # ============================================
    print("\n【测试 4：订单操作】")
    print("-" * 60)

    # 创建测试订单
    test_order = {
        "order_no": "ORD20240115-TEST",
        "user_id": 2,
        "items": [
            {"product_id": 1, "name": "iPhone 15 Pro", "price": 8999, "quantity": 1, "subtotal": 8999},
        ],
        "total_price": 8999,
        "status": "待支付",
        "created_at": "2024-01-15 12:00:00",
        "updated_at": "2024-01-15 12:00:00"
    }
    store.add_order(test_order)
    print(f"  订单已添加：{test_order['order_no']}")

    # 查询订单
    order = store.get_order_by_no("ORD20240115-TEST")
    print(f"  查询订单：{order['order_no']} - {order['status']}")

    # 更新状态
    store.update_order_status("ORD20240115-TEST", "已支付")
    order = store.get_order_by_no("ORD20240115-TEST")
    print(f"  更新状态：{order['order_no']} - {order['status']}")

    # 按用户查询
    user_orders = store.get_orders_by_user(2)
    print(f"  用户 2 的订单数：{len(user_orders)}")

    # ============================================
    # 测试 5：配置操作
    # ============================================
    print("\n【测试 5：配置操作】")
    print("-" * 60)

    print(f"  站点名称：{store.get_config('site_name')}")
    print(f"  分页大小：{store.get_config('page_size')}")
    print(f"  不存在的键：{store.get_config('not_exist', '默认值')}")

    store.set_config("theme", "dark")
    print(f"  新增配置：theme = {store.get_config('theme')}")

    # ============================================
    # 测试 6：备份和恢复
    # ============================================
    print("\n【测试 6：数据备份】")
    print("-" * 60)

    backup_path = store.backup("backup")
    print(f"  备份路径：{backup_path}")

    # ============================================
    # 测试 7：统计信息
    # ============================================
    print("\n【测试 7：数据统计】")
    print("-" * 60)

    stats = store.get_stats()
    for key, value in stats.items():
        print(f"  {key}：{value}")

    # ============================================
    # 测试 8：异常场景
    # ============================================
    print("\n【测试 8：异常场景】")
    print("-" * 60)

    # 查询不存在的商品
    result = store.get_product_by_id(999)
    print(f"  查询不存在的商品：{result}")

    # 搜索无结果
    results = store.search_products("xyz不存在")
    print(f"  搜索无结果：{len(results)} 个")

    # 库存不足时扣减
    store.update_product_stock(1, -99999)
    print(f"  库存不足扣减：已打印错误信息")

    # 登录失败
    result = store.verify_login("nobody", "xxx")
    print(f"  不存在的用户登录：{result['message']}")

    # 订单不存在
    order = store.get_order_by_no("ORD不存在")
    print(f"  查询不存在的订单：{order}")

    print(f"\n{'=' * 60}")
    print("DataStore 测试完成")
    print(f"{'=' * 60}")