"""
MallLite 表单验证
使用正则表达式验证各种输入数据
"""

import re


class Validator:
    """表单验证器"""

    @staticmethod
    def is_valid_phone(phone):
        """
        验证手机号格式

        规则：1 开头，第二位 3-9，后面 9 位数字
        """
        if not phone:
            return False
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone))

    @staticmethod
    def is_valid_email(email):
        """验证邮箱格式"""
        if not email:
            return False
        pattern = r"^[\w.-]+@[\w.-]+\.\w{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_username(username):
        """
        验证用户名格式

        规则：3-20 位，字母数字下划线，以字母开头
        """
        if not username:
            return False
        pattern = r"^[a-zA-Z]\w{2,19}$"
        return bool(re.match(pattern, username))

    @staticmethod
    def is_valid_password(password):
        """
        验证密码强度

        规则：6-20 位，至少包含字母和数字
        """
        if not password:
            return False
        if len(password) < 6 or len(password) > 20:
            return False
        has_letter = bool(re.search(r"[a-zA-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        return has_letter and has_digit

    @staticmethod
    def is_positive_number(value):
        """验证是否为正数"""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_price(price):
        """验证价格（正数，最多两位小数）"""
        if not isinstance(price, (int, float)):
            return False
        return price > 0 and round(price, 2) == price

    @staticmethod
    def sanitize_string(text, max_length=200):
        """
        清理字符串：去除首尾空格，限制长度

        参数：
            text: 输入文本
            max_length: 最大长度

        返回：
            清理后的字符串
        """
        if not isinstance(text, str):
            return ""
        text = text.strip()
        if len(text) > max_length:
            text = text[:max_length]
        return text

    @classmethod
    def validate_register_form(cls, data):
        """
        验证注册表单

        参数：
            data: 包含 username, password, phone, email 的字典

        返回：
            (is_valid, errors) 元组
        """
        errors = []

        username = data.get("username", "")
        if not cls.is_valid_username(username):
            errors.append("用户名需 3-20 位，字母开头，只含字母数字下划线")

        password = data.get("password", "")
        if not cls.is_valid_password(password):
            errors.append("密码需 6-20 位，至少包含字母和数字")

        phone = data.get("phone", "")
        if phone and not cls.is_valid_phone(phone):
            errors.append("手机号格式不正确")

        email = data.get("email", "")
        if email and not cls.is_valid_email(email):
            errors.append("邮箱格式不正确")

        return len(errors) == 0, errors

    @classmethod
    def validate_login_form(cls, data):
        """验证登录表单"""
        errors = []

        if not data.get("username"):
            errors.append("请输入用户名")

        if not data.get("password"):
            errors.append("请输入密码")

        return len(errors) == 0, errors

    @classmethod
    def validate_product_form(cls, data):
        """验证商品表单"""
        errors = []

        name = cls.sanitize_string(data.get("name", ""))
        if not name:
            errors.append("商品名称不能为空")

        price = data.get("price")
        if price is None or not cls.is_valid_price(price):
            errors.append("价格必须为正数，最多两位小数")

        stock = data.get("stock")
        if stock is None or not isinstance(stock, int) or stock < 0:
            errors.append("库存必须为非负整数")

        category = data.get("category", "")
        valid_categories = ["手机", "笔记本", "平板", "配件"]
        if category not in valid_categories:
            errors.append(f"分类必须是以下之一：{', '.join(valid_categories)}")

        return len(errors) == 0, errors