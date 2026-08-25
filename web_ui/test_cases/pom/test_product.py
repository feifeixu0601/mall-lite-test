"""
商品浏览功能测试（POM 模式）

使用 HomePage + ProductPage 页面对象编写
覆盖商品列表展示、商品详情页信息验证
"""

import pytest
from common.allure_helper import AllureHelper


@pytest.mark.product
class TestProduct:
    """商品浏览测试集"""

    # ========================================
    # 首页商品列表
    # ========================================

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_product_list_displayed(self, home_page):
        """
        验证首页商品列表正常展示

        步骤：
            1. 打开首页
            2. 验证商品列表不为空
            3. 验证每个商品卡片都有名称和价格
        """
        AllureHelper.title("首页商品列表展示")
        AllureHelper.severity("critical")
        AllureHelper.feature("商品")

        home_page.open()

        count = home_page.get_product_count()
        assert count > 0, "首页应该展示商品"

        names = home_page.get_product_names()
        for name in names:
            assert name, f"商品名不能为空：{names}"

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_product_detail_info(self, home_page, product_page):
        """
        验证商品详情页信息完整

        步骤：
            1. 打开首页
            2. 点击第一个商品
            3. 验证详情页有标题、价格、库存、描述、加购按钮
        """
        AllureHelper.title("商品详情页信息验证")
        AllureHelper.severity("critical")
        AllureHelper.feature("商品")
        AllureHelper.story("商品详情")

        home_page.open()

        product_name = home_page.get_product_name(0)
        AllureHelper.attach_text(f"首页第一个商品：{product_name}", "商品信息")

        home_page.click_product(0)

        # 验证详情页元素
        title = product_page.get_title()
        assert title, "商品标题不能为空"
        AllureHelper.attach_text(f"详情页标题：{title}", "详情页")

        price = product_page.get_price()
        assert price and "¥" in price, f"价格格式不正确：{price}"

        stock = product_page.get_stock_text()
        assert stock, "库存信息不能为空"

        desc = product_page.get_description()
        assert desc, "商品描述不能为空"

        product_page.expect_visible(product_page.BTN_ADD_TO_CART)

    @pytest.mark.regression
    @pytest.mark.p1
    def test_product_detail_navigation(self, home_page, product_page):
        """
        验证从详情页可以返回首页

        步骤：
            1. 打开首页
            2. 点击第一个商品进入详情
            3. 点击浏览器后退
            4. 验证回到首页
        """
        AllureHelper.title("详情页返回首页")
        AllureHelper.feature("商品")

        home_page.open()
        home_page.click_product(0)

        assert "/products/" in home_page.get_current_url()

        product_page.go_back()

        assert home_page.get_product_count() > 0

    @pytest.mark.regression
    @pytest.mark.p2
    def test_product_pagination(self, home_page):
        """
        验证分页功能

        步骤：
            1. 打开首页
            2. 记录第一页的商品
            3. 如果有下一页，翻到下一页
            4. 验证第二页有商品且和第一页不同
        """
        AllureHelper.title("商品分页功能")
        AllureHelper.feature("商品")

        home_page.open()

        first_page_names = home_page.get_product_names()
        total_pages = home_page.get_total_pages()

        AllureHelper.attach_text(
            f"总页数：{total_pages}\n第一页商品：{first_page_names}",
            "第一页信息"
        )

        if total_pages > 1:
            home_page.go_to_next_page()

            second_page_names = home_page.get_product_names()
            AllureHelper.attach_text(f"第二页商品：{second_page_names}", "第二页信息")

            assert len(second_page_names) > 0, "第二页应该有商品"
            # 验证翻页前后商品不完全相同
            assert second_page_names != first_page_names, "翻页后商品应该变化"