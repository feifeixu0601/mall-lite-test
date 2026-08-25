"""
OrderPage - 订单页面对象
"""

import allure
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger("order_page")


class OrderPage(BasePage):
    """
    订单页面对象

    页面地址：/orders

    封装的操作：
    - open()：打开订单列表
    - get_order_count()：获取订单数量
    - get_order_no(index)：获取第 N 个订单号
    - get_order_status(index)：获取第 N 个订单状态
    - has_order(order_no)：判断是否存在某个订单
    """

    URL = "/orders"

    # ========================================
    # 元素定位
    # ========================================

    LIST_ORDER = "#order-list"
    CARD_ORDER = ".order-card"
    TEXT_ORDER_NO = ".order-no"
    TEXT_ORDER_STATUS = ".order-status"
    TEXT_ORDER_TOTAL = ".order-total"
    TEXT_ORDER_TIME = ".order-time"
    DIV_EMPTY = "#empty-orders"

    # ========================================
    # 页面操作
    # ========================================

    def open(self):
        """打开订单页"""
        logger.info("打开订单页")
        self.navigate()

    # ========================================
    # 结果获取
    # ========================================

    def get_order_count(self) -> int:
        """获取订单数量"""
        count = self.get_element_count(self.CARD_ORDER)
        logger.info(f"订单数量：{count}")
        return count

    def get_order_no(self, index=0) -> str:
        """获取第 N 个订单号"""
        return self.page.locator(self.TEXT_ORDER_NO).nth(index).text_content().strip()

    def get_order_status(self, index=0) -> str:
        """获取第 N 个订单状态"""
        return self.page.locator(self.TEXT_ORDER_STATUS).nth(index).text_content().strip()

    def get_order_total(self, index=0) -> str:
        """获取第 N 个订单金额"""
        return self.page.locator(self.TEXT_ORDER_TOTAL).nth(index).text_content().strip()

    def get_all_order_nos(self) -> list:
        """获取所有订单号"""
        nos = []
        for i in range(self.get_order_count()):
            nos.append(self.get_order_no(i))
        return nos

    def has_order(self, order_no) -> bool:
        """
        判断是否存在某个订单

        参数：
            order_no: 订单号
        """
        return order_no in self.get_all_order_nos()

    def is_empty(self) -> bool:
        """判断订单列表是否为空"""
        return self.is_visible(self.DIV_EMPTY) or self.get_order_count() == 0