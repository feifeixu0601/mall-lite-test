"""
CartPage - 购物车页面对象
"""

import allure
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger("cart_page")


class CartPage(BasePage):
    """
    购物车页面对象

    页面地址：/cart

    封装的操作：
    - open()：打开购物车
    - get_cart_items()：获取所有购物车商品
    - get_item_count()：获取商品种类数
    - get_total_price()：获取总价
    - delete_item(index)：删除第 N 个商品
    - checkout()：去结算
    - is_empty()：购物车是否为空
    - clear_cart()：清空购物车          ← 新增
    """

    URL = "/cart"

    # ========================================
    # 元素定位
    # ========================================

    LIST_CART = "#cart-list"
    ITEM_CART = ".cart-item"
    ITEM_NAME = ".item-name"
    ITEM_PRICE = ".item-price"
    ITEM_QUANTITY = ".item-quantity"
    ITEM_SUBTOTAL = ".item-subtotal"
    BTN_DELETE = ".delete-btn"
    TEXT_TOTAL = "#total-price"
    BTN_CHECKOUT = "#checkout-btn"
    DIV_EMPTY = "#empty-cart"

    # ========================================
    # 页面操作
    # ========================================

    def open(self):
        """打开购物车页"""
        logger.info("打开购物车")
        self.navigate()

    def delete_item(self, index=0):
        """
        删除第 N 个商品

        参数：
            index: 商品索引（从 0 开始）
        """
        item_name = self.get_item_name(index)
        logger.info(f"删除购物车商品：{item_name}")
        self.page.locator(self.ITEM_CART).nth(index).locator(self.BTN_DELETE).click()

    def clear_cart(self):                          # ← 新增方法
        """
        清空购物车（逐个删除所有商品）

        用法：
            cart_page.clear_cart()
        """
        count = self.get_item_count()
        if count == 0:
            logger.info("购物车已为空，无需清空")
            return
        logger.info(f"清空购物车，共 {count} 个商品")
        for _ in range(count):
            if self.get_item_count() > 0:
                self.delete_item(0)
                self.page.wait_for_timeout(500)
        logger.info("购物车已清空")

    def checkout(self):
        """
        点击去结算

        用法：
            cart_page.checkout()
        """
        logger.info("点击去结算")
        self.click(self.BTN_CHECKOUT)

    # ========================================
    # 结果获取
    # ========================================

    def get_item_count(self) -> int:
        """
        获取购物车商品种类数

        返回：
            种类数（不同商品有几种）
        """
        count = self.get_element_count(self.ITEM_CART)
        logger.info(f"购物车商品种类：{count}")
        return count

    def get_item_name(self, index=0) -> str:
        """获取第 N 个商品的名称"""
        return self.page.locator(self.ITEM_NAME).nth(index).text_content().strip()

    def get_item_names(self) -> list:
        """获取所有商品名"""
        names = []
        for i in range(self.get_item_count()):
            names.append(self.get_item_name(i))
        return names

    def get_total_price(self) -> str:
        """
        获取总价文本

        返回：
            如 "¥8999"
        """
        if self.element_exists(self.TEXT_TOTAL):
            return self.get_text(self.TEXT_TOTAL)
        return "¥0"

    def get_total_price_number(self) -> float:
        """获取总价数字"""
        text = self.get_total_price()
        return float(text.replace("合计：¥", "").replace("¥", "").replace(",", ""))

    def is_empty(self) -> bool:
        """
        判断购物车是否为空

        返回：
            True/False
        """
        empty = self.is_visible(self.DIV_EMPTY) or self.get_item_count() == 0
        logger.info(f"购物车{'为空' if empty else '不为空'}")
        return empty

    def has_item(self, product_name) -> bool:
        """
        判断购物车中是否包含某商品

        参数：
            product_name: 商品名称

        返回：
            True/False
        """
        names = self.get_item_names()
        return any(product_name in name for name in names)