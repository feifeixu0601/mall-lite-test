"""
OrderKeywords - 订单业务关键字
"""

from common.logger import get_logger
from pages.order_page import OrderPage

logger = get_logger("order_keywords")


class OrderKeywords:
    """订单业务关键字"""

    def __init__(self, page):
        self.page = page
        self.order_page = OrderPage(page)

    def open_orders(self):
        """
        打开订单页

        YAML 用法：
            - keyword: open_orders
        """
        logger.info("[业务关键字] 打开订单页")
        self.order_page.open()

    def assert_orders_not_empty(self):
        """
        断言订单列表不为空

        YAML 用法：
            - keyword: assert_orders_not_empty
        """
        assert not self.order_page.is_empty(), "订单列表不应该为空"

    def assert_order_count_min(self, min_count):
        """
        断言订单数量至少为 N

        YAML 用法：
            - keyword: assert_order_count_min
              params:
                min_count: 1
        """
        actual = self.order_page.get_order_count()
        assert actual >= int(min_count), \
            f"期望至少 {min_count} 个订单，实际 {actual} 个"

    def assert_order_has_info(self, index=0):
        """
        断言订单信息完整

        YAML 用法：
            - keyword: assert_order_has_info
              params:
                index: 0
        """
        order_no = self.order_page.get_order_no(int(index))
        assert order_no and "ORD" in order_no, f"订单号不正确：{order_no}"

        status = self.order_page.get_order_status(int(index))
        assert status, "订单状态不能为空"

        total = self.order_page.get_order_total(int(index))
        assert total, "订单金额不能为空"