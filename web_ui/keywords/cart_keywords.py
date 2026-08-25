"""
CartKeywords - 购物车业务关键字
"""

from common.logger import get_logger
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage

logger = get_logger("cart_keywords")


class CartKeywords:
    """购物车业务关键字"""

    def __init__(self, page):
        self.page = page
        self.home_page = HomePage(page)
        self.product_page = ProductPage(page)
        self.cart_page = CartPage(page)

    def open_product_detail(self, product_id):
        """
        打开商品详情页

        YAML 用法：
            - keyword: open_product_detail
              params:
                product_id: 1
        """
        logger.info(f"[业务关键字] 打开商品详情：ID={product_id}")
        self.product_page.open(int(product_id))

    def add_to_cart(self):
        """
        在商品详情页加入购物车

        YAML 用法：
            - keyword: add_to_cart
        """
        logger.info("[业务关键字] 加入购物车")
        self.product_page.add_to_cart()

    def add_product_from_home(self, index=0):
        """
        从首页直接添加商品到购物车

        YAML 用法：
            - keyword: add_product_from_home
              params:
                index: 0
        """
        logger.info(f"[业务关键字] 从首页添加第 {int(index) + 1} 个商品到购物车")
        self.home_page.add_product_to_cart(int(index))

    def open_cart(self):
        """
        打开购物车页

        YAML 用法：
            - keyword: open_cart
        """
        logger.info("[业务关键字] 打开购物车")
        self.cart_page.open()

    def clear_cart(self):                      # ← 新增
        """
        清空购物车

        YAML 用法：
            - keyword: clear_cart
        """
        logger.info("[业务关键字] 清空购物车")
        self.cart_page.clear_cart()

    def delete_cart_item(self, index=0):
        """
        删除购物车中第 N 个商品

        YAML 用法：
            - keyword: delete_cart_item
              params:
                index: 0
        """
        logger.info(f"[业务关键字] 删除购物车第 {int(index) + 1} 个商品")
        self.cart_page.delete_item(int(index))

    def checkout(self):
        """
        去结算

        YAML 用法：
            - keyword: checkout
        """
        logger.info("[业务关键字] 去结算")
        self.cart_page.checkout()

    def assert_cart_not_empty(self):
        """
        断言购物车不为空

        YAML 用法：
            - keyword: assert_cart_not_empty
        """
        assert not self.cart_page.is_empty(), "购物车不应该为空"

    def assert_cart_empty(self):
        """
        断言购物车为空

        YAML 用法：
            - keyword: assert_cart_empty
        """
        assert self.cart_page.is_empty(), "购物车应该为空"

    def assert_cart_contains(self, product_name):
        """
        断言购物车包含某商品

        YAML 用法：
            - keyword: assert_cart_contains
              params:
                product_name: "iPhone 15 Pro"
        """
        assert self.cart_page.has_item(product_name), \
            f"购物车中应该包含 '{product_name}'"

    def assert_cart_item_count(self, expected_count):
        """
        断言购物车商品种类数

        YAML 用法：
            - keyword: assert_cart_item_count
              params:
                expected_count: 2
        """
        actual = self.cart_page.get_item_count()
        assert actual >= int(expected_count), \
            f"购物车期望至少 {expected_count} 种商品，实际 {actual} 种"