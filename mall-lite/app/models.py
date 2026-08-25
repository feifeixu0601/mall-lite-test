"""
MallLite 数据模型
定义系统中所有数据对象的类
"""

from datetime import datetime


class User:
    """用户模型"""

    def __init__(self, id, username, password, phone="", email="", role="user", nickname=""):
        self.id = id
        self.username = username
        self.password = password
        self.phone = phone
        self.email = email
        self.role = role
        self.nickname = nickname or username

    def to_dict(self, include_password=False):
        """转为字典（用于 JSON 响应）"""
        data = {
            "id": self.id,
            "username": self.username,
            "phone": self.phone,
            "email": self.email,
            "role": self.role,
            "nickname": self.nickname,
        }
        if include_password:
            data["password"] = self.password
        return data

    def check_password(self, password):
        return self.password == password

    @staticmethod
    def from_dict(data):
        """从字典创建 User 对象"""
        return User(**data)


class Product:
    """商品模型"""

    def __init__(self, id, name, price, category, stock, description="", is_new=False, rating=0.0):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.stock = stock
        self.description = description
        self.is_new = is_new
        self.rating = rating

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "stock": self.stock,
            "description": self.description,
            "is_new": self.is_new,
            "rating": self.rating,
        }

    def is_in_stock(self, quantity=1):
        return self.stock >= quantity

    def reduce_stock(self, quantity):
        if not self.is_in_stock(quantity):
            return False
        self.stock -= quantity
        return True

    @staticmethod
    def from_dict(data):
        return Product(**data)


class CartItem:
    """购物车项"""

    def __init__(self, product_id, name, price, quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    @property
    def subtotal(self):
        return self.price * self.quantity

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal,
        }


class Order:
    """订单模型"""

    def __init__(self, order_no, user_id, items, total_price, status="待支付"):
        self.order_no = order_no
        self.user_id = user_id
        self.items = items  # list of CartItem
        self.total_price = total_price
        self.status = status
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at

    def to_dict(self):
        return {
            "order_no": self.order_no,
            "user_id": self.user_id,
            "items": [item.to_dict() if isinstance(item, CartItem) else item for item in self.items],
            "total_price": self.total_price,
            "total_quantity": sum(
                item.quantity if isinstance(item, CartItem) else item["quantity"]
                for item in self.items
            ),
            "item_count": len(self.items),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def pay(self):
        if self.status != "待支付":
            return False
        self.status = "已支付"
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def cancel(self):
        if self.status in ["已取消", "已完成"]:
            return False
        self.status = "已取消"
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True