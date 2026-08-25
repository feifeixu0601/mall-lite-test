"""
SearchKeywords - 搜索业务关键字
"""

from common.logger import get_logger
from pages.home_page import HomePage

logger = get_logger("search_keywords")


class SearchKeywords:
    """搜索业务关键字"""

    def __init__(self, page):
        self.page = page
        self.home_page = HomePage(page)

    def open_home_page(self):
        """
        打开首页

        YAML 用法：
            - keyword: open_home_page
        """
        logger.info("[业务关键字] 打开首页")
        self.home_page.open()

    def search(self, keyword):
        """
        搜索商品

        YAML 用法：
            - keyword: search
              params:
                keyword: "iPhone"
        """
        logger.info(f"[业务关键字] 搜索：{keyword}")
        self.home_page.search(keyword)

    def click_category(self, category):
        """
        点击分类筛选

        YAML 用法：
            - keyword: click_category
              params:
                category: "手机"
        """
        logger.info(f"[业务关键字] 分类筛选：{category}")
        self.home_page.click_category(category)

    def click_product(self, index=0):
        """
        点击第 N 个商品

        YAML 用法：
            - keyword: click_product
              params:
                index: 0
        """
        logger.info(f"[业务关键字] 点击第 {int(index) + 1} 个商品")
        self.home_page.click_product(int(index))

    def assert_product_count(self, expected_count):
        """
        断言商品数量

        YAML 用法：
            - keyword: assert_product_count
              params:
                expected_count: 8
        """
        actual = self.home_page.get_product_count()
        assert actual == int(expected_count), \
            f"期望 {expected_count} 个商品，实际 {actual} 个"

    def assert_product_count_min(self, min_count):
        """
        断言商品数量至少为 N

        YAML 用法：
            - keyword: assert_product_count_min
              params:
                min_count: 1
        """
        actual = self.home_page.get_product_count()
        assert actual >= int(min_count), \
            f"期望至少 {min_count} 个商品，实际 {actual} 个"

    def assert_products_not_empty(self):
        """
        断言商品列表不为空

        YAML 用法：
            - keyword: assert_products_not_empty
        """
        assert self.home_page.has_products(), "商品列表不应该为空"

    def assert_products_empty(self):
        """
        断言商品列表为空

        YAML 用法：
            - keyword: assert_products_empty
        """
        assert self.home_page.is_empty(), "商品列表应该为空"