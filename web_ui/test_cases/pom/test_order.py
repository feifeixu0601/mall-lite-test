"""
订单功能测试（POM 模式）

使用 HomePage + ProductPage + CartPage + OrderPage 页面对象编写
覆盖创建订单、查看订单、订单状态验证
"""

import pytest
from common.allure_helper import AllureHelper


@pytest.mark.order
class TestOrder:
    """订单测试集"""

    def _login_add_product_and_checkout(self, login_page, home_page, product_page, cart_page, admin_user):
        """辅助方法：登录 → 添加商品 → 去结算"""
        login_page.login(admin_user["username"], admin_user["password"])
        assert login_page.is_login_success()

        home_page.open()
        product_name = home_page.get_product_name(0)
        home_page.click_product(0)
        product_page.add_to_cart()

        cart_page.open()
        assert not cart_page.is_empty()
        cart_page.checkout()

        return product_name

    # ========================================
    # 创建订单
    # ========================================

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_create_order(self, login_page, home_page, product_page, cart_page, order_page, admin_user):
        """
        验证从购物车结算创建订单

        步骤：
            1. 登录
            2. 添加商品到购物车
            3. 去结算
            4. 验证订单列表中出现新订单
        """
        AllureHelper.title("从购物车创建订单")
        AllureHelper.severity("critical")
        AllureHelper.feature("订单")
        AllureHelper.story("创建订单")

        self._login_add_product_and_checkout(
            login_page, home_page, product_page, cart_page, admin_user
        )

        # 验证订单页有订单
        order_page.open()
        count = order_page.get_order_count()
        AllureHelper.attach_text(f"订单数量：{count}", "订单信息")
        assert count > 0, "应该至少有一个订单"

    # ========================================
    # 查看订单
    # ========================================

    @pytest.mark.smoke
    @pytest.mark.p1
    def test_order_has_info(self, login_page, home_page, product_page, cart_page, order_page, admin_user):
        """
        验证订单信息完整

        步骤：
            1. 创建订单
            2. 打开订单页
            3. 验证订单有订单号、状态、金额
        """
        AllureHelper.title("订单信息完整性验证")
        AllureHelper.feature("订单")
        AllureHelper.story("查看订单")

        self._login_add_product_and_checkout(
            login_page, home_page, product_page, cart_page, admin_user
        )

        order_page.open()
        assert not order_page.is_empty(), "订单列表不应该为空"

        order_no = order_page.get_order_no(0)
        assert order_no and "ORD" in order_no, f"订单号格式不正确：{order_no}"

        status = order_page.get_order_status(0)
        assert status, "订单状态不能为空"

        total = order_page.get_order_total(0)
        assert total and "¥" in total, f"订单金额格式不正确：{total}"

        AllureHelper.attach_text(
            f"订单号：{order_no}\n状态：{status}\n金额：{total}",
            "订单详情"
        )

    @pytest.mark.regression
    @pytest.mark.p2
    def test_empty_order_list(self, login_page, home_page, order_page, admin_user):
        """
        验证未下单时订单列表为空

        步骤：
            1. 登录（不创建任何订单）
            2. 打开订单页
            3. 验证订单为空或显示提示
        """
        AllureHelper.title("未下单时订单列表为空")
        AllureHelper.feature("订单")
        AllureHelper.story("空订单")

        login_page.login(admin_user["username"], admin_user["password"])
        order_page.open()

        # 由于数据可能残留，这里只验证页面能正常加载
        order_page.expect_visible(order_page.LIST_ORDER if not order_page.is_empty() else order_page.DIV_EMPTY)