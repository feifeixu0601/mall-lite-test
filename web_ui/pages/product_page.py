"""
ProductPage - 商品详情页面对象
"""

import allure
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger("product_page")


class ProductPage(BasePage):
    """
    商品详情页面对象

    页面地址：/products/{product_id}

    封装的操作：
    - open(product_id)：打开商品详情
    - get_title()：获取商品名称
    - get_price()：获取商品价格
    - get_stock()：获取库存信息
    - set_quantity(num)：设置购买数量
    - add_to_cart()：加入购物车
    - get_toast_message()：获取提示信息
    """

    # ========================================
    # 元素定位
    # ========================================

    TEXT_TITLE = "#product-title"
    TEXT_PRICE = "#product-price"
    TEXT_STOCK = "#product-stock"
    TEXT_DESC = "#product-desc"

    INPUT_QUANTITY = "#qty-input"
    BTN_MINUS = "#qty-minus"
    BTN_PLUS = "#qty-plus"
    BTN_ADD_TO_CART = "#add-to-cart-btn"

    # ========================================
    # 页面操作
    # ========================================

    def open(self, product_id):
        """
        打开商品详情页

        参数：
            product_id: 商品 ID

        用法：
            product_page.open(1)  # 打开 ID=1 的商品
        """
        logger.info(f"打开商品详情：ID={product_id}")
        self.page.goto(f"/products/{product_id}")
        self.wait_for_load()

    def get_title(self) -> str:
        """获取商品名称"""
        return self.get_text(self.TEXT_TITLE)

    def get_price(self) -> str:
        """获取商品价格（带 ￥ 符号）"""
        return self.get_text(self.TEXT_PRICE)

    def get_price_number(self) -> float:
        """获取商品价格（纯数字）"""
        price_text = self.get_price()
        return float(price_text.replace("¥", "").replace(",", ""))

    def get_stock_text(self) -> str:
        """获取库存文本"""
        return self.get_text(self.TEXT_STOCK)

    def get_description(self) -> str:
        """获取商品描述"""
        return self.get_text(self.TEXT_DESC)

    def set_quantity(self, num):
        """
        设置购买数量

        参数：
            num: 数量
        """
        logger.info(f"设置数量：{num}")
        self.fill(self.INPUT_QUANTITY, str(num))

    def get_quantity(self) -> int:
        """获取当前数量"""
        return int(self.get_value(self.INPUT_QUANTITY))

    def click_plus(self, times=1):
        """
        点击加号增加数量

        参数：
            times: 点击次数
        """
        for _ in range(times):
            self.click(self.BTN_PLUS)

    def click_minus(self, times=1):
        """点击减号减少数量"""
        for _ in range(times):
            self.click(self.BTN_MINUS)

    def add_to_cart(self):
        """
        点击加入购物车

        用法：
            product_page.open(1)
            product_page.add_to_cart()
        """
        logger.info("点击加入购物车")
        self.click(self.BTN_ADD_TO_CART)

    def buy_now(self):
        """点击立即购买"""
        logger.info("点击立即购买")
        # MallLite 的立即购买按钮（如果有的话）
        if self.element_exists(".buy-now-btn"):
            self.click(".buy-now-btn")

    def is_add_cart_success(self) -> bool:
        """
        判断加入购物车是否成功

        判断依据：页面跳转到了购物车页 或 显示成功提示
        """
        # 方式 1：跳转到了购物车页
        if "/cart" in self.get_current_url():
            return True
        # 方式 2：显示了 Toast 提示
        if self.is_visible(".toast"):
            toast_text = self.get_text(".toast")
            return "成功" in toast_text or "已" in toast_text
        return False