"""
HomePage - 首页页面对象
封装首页的元素定位和操作
"""

import allure
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger("home_page")


class HomePage(BasePage):
    """
    首页页面对象

    页面地址：/（根路径）

    封装的操作：
    - search(keyword)：搜索商品
    - click_category(name)：点击分类
    - get_product_names()：获取当前页所有商品名
    - get_product_count()：获取当前页商品数量
    - click_product(index)：点击第 N 个商品
    - add_product_to_cart(index)：将第 N 个商品加入购物车
    - go_to_next_page()：翻下一页
    - go_to_cart()：进入购物车
    """

    URL = "/"

    # ========================================
    # 元素定位
    # ========================================

    # 搜索
    INPUT_SEARCH = "#search-input"
    BTN_SEARCH = "#search-btn"

    # 分类
    NAV_CATEGORY = "#category-nav"
    LINK_CATEGORY = ".category-link"

    # 商品列表
    LIST_PRODUCT = "#product-list"
    CARD_PRODUCT = ".product-card"
    CARD_PRODUCT_NAME = ".product-card .product-name"
    CARD_PRODUCT_PRICE = ".product-card .product-price"
    CARD_ADD_CART_BTN = ".add-cart-btn"

    # 翻页
    BTN_PREV_PAGE = ".page-prev"
    BTN_NEXT_PAGE = ".page-next"
    TEXT_PAGE_INFO = "#page-info"

    # 导航
    LINK_CART = "#cart-link"
    LINK_ORDERS = "#orders-link"
    LINK_PROFILE = "#profile-link"
    LINK_LOGIN = "#login-link"

    # ========================================
    # 页面操作
    # ========================================

    def open(self):
        """打开首页"""
        logger.info("打开首页")
        self.navigate()

    def search(self, keyword):
        """
        搜索商品

        参数：
            keyword: 搜索关键词

        用法：
            home_page.search("iPhone")
        """
        logger.info(f"搜索商品：{keyword}")
        self.fill(self.INPUT_SEARCH, keyword)
        self.click(self.BTN_SEARCH)
        self.wait_for_load("networkidle")

    def click_category(self, category_name):
        """
        点击分类

        参数：
            category_name: 分类名称（如 "手机"、"笔记本"）

        用法：
            home_page.click_category("手机")
        """
        logger.info(f"点击分类：{category_name}")
        self.page.locator(f'.category-link:has-text("{category_name}")').click()
        self.wait_for_load("networkidle")

    def click_product(self, index=0):
        """
        点击第 N 个商品（从 0 开始）

        参数：
            index: 商品索引

        用法：
            home_page.click_product(0)  # 点击第一个商品
        """
        logger.info(f"点击第 {index + 1} 个商品")
        self.page.locator(self.CARD_PRODUCT).nth(index).click()

    def add_product_to_cart(self, index=0):
        """
        将第 N 个商品加入购物车

        参数：
            index: 商品索引

        用法：
            home_page.add_product_to_cart(0)
        """
        product_name = self.get_product_name(index)
        logger.info(f"加入购物车：{product_name}")
        self.page.locator(self.CARD_PRODUCT).nth(index).locator(self.CARD_ADD_CART_BTN).click()

    def go_to_next_page(self):
        """翻到下一页"""
        if self.element_exists(self.BTN_NEXT_PAGE):
            logger.info("翻到下一页")
            self.click(self.BTN_NEXT_PAGE)
            self.wait_for_load("networkidle")
        else:
            logger.warning("没有下一页了")

    def go_to_prev_page(self):
        """翻到上一页"""
        if self.element_exists(self.BTN_PREV_PAGE):
            self.click(self.BTN_PREV_PAGE)
            self.wait_for_load("networkidle")

    def go_to_cart(self):
        """进入购物车"""
        logger.info("进入购物车")
        self.click(self.LINK_CART)

    def go_to_orders(self):
        """进入订单页"""
        self.click(self.LINK_ORDERS)

    def go_to_profile(self):
        """进入个人中心"""
        self.click(self.LINK_PROFILE)

    def go_to_login(self):
        """进入登录页"""
        self.click(self.LINK_LOGIN)

    # ========================================
    # 结果获取
    # ========================================

    def get_product_count(self) -> int:
        """
        获取当前页商品数量

        返回：
            商品数量

        用法：
            count = home_page.get_product_count()
            assert count > 0
        """
        count = self.get_element_count(self.CARD_PRODUCT)
        logger.info(f"当前页商品数量：{count}")
        return count

    def get_product_names(self) -> list:
        """
        获取当前页所有商品名

        返回：
            商品名列表

        用法：
            names = home_page.get_product_names()
            assert "iPhone 15 Pro" in names
        """
        names = []
        count = self.get_product_count()
        for i in range(count):
            name = self.page.locator(self.CARD_PRODUCT_NAME).nth(i).text_content()
            names.append(name.strip())
        logger.info(f"商品列表：{names}")
        return names

    def get_product_name(self, index=0) -> str:
        """获取第 N 个商品的名称"""
        return self.page.locator(self.CARD_PRODUCT_NAME).nth(index).text_content().strip()

    def get_product_price(self, index=0) -> str:
        """获取第 N 个商品的价格（字符串）"""
        return self.page.locator(self.CARD_PRODUCT_PRICE).nth(index).text_content().strip()

    def get_page_info(self) -> str:
        """获取翻页信息"""
        if self.element_exists(self.TEXT_PAGE_INFO):
            return self.get_text(self.TEXT_PAGE_INFO)
        return ""

    def get_current_page(self) -> int:
        """获取当前页码"""
        info = self.get_page_info()
        if "第" in info and "/" in info:
            try:
                return int(info.split("第")[1].split("/")[0])
            except (ValueError, IndexError):
                pass
        return 1

    def get_total_pages(self) -> int:
        """获取总页数"""
        info = self.get_page_info()
        if "/" in info:
            try:
                return int(info.split("/")[1].split("页")[0])
            except (ValueError, IndexError):
                pass
        return 1

    def has_products(self) -> bool:
        """当前页是否有商品"""
        return self.get_product_count() > 0

    def is_empty(self) -> bool:
        """当前页是否无商品"""
        return self.get_product_count() == 0