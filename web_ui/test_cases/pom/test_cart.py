"""
购物车功能测试（POM 模式）

使用 HomePage + ProductPage + CartPage 页面对象编写
覆盖添加、删除、数量修改、空状态、合计金额
"""

import pytest
from common.allure_helper import AllureHelper


@pytest.mark.cart
class TestCart:
    """购物车测试集"""

    def _login_and_go_home(self, login_page, home_page, admin_user):
        """辅助方法：登录并回到首页"""
        login_page.login(admin_user["username"], admin_user["password"])
        assert login_page.is_login_success()
        home_page.open()

    def _clear_cart(self, cart_page):
        """辅助方法：清空购物车，确保干净的测试环境"""
        cart_page.open()
        cart_page.clear_cart()

    # ========================================
    # 添加购物车
    # ========================================

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_add_product_to_cart(self, login_page, home_page, product_page, cart_page, admin_user):
        """
        验证从商品详情页添加商品到购物车

        步骤：
            1. 登录
            2. 打开首页，点击第一个商品
            3. 在详情页点击加入购物车
            4. 验证购物车中有该商品
        """
        AllureHelper.title("从详情页添加商品到购物车")
        AllureHelper.severity("critical")
        AllureHelper.feature("购物车")
        AllureHelper.story("添加商品")

        self._login_and_go_home(login_page, home_page, admin_user)
        self._clear_cart(cart_page)

        home_page.open()
        product_name = home_page.get_product_name(0)
        AllureHelper.attach_text(f"目标商品：{product_name}", "商品信息")

        home_page.click_product(0)
        product_page.add_to_cart()

        cart_page.open()
        assert not cart_page.is_empty(), "购物车不应该为空"
        assert cart_page.has_item(product_name), \
            f"购物车中应该包含 '{product_name}'"

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_add_from_homepage(self, login_page, home_page, cart_page, admin_user):
        """
        验证从首页直接添加商品到购物车

        步骤：
            1. 登录
            2. 在首页点击第一个商品的"加入购物车"按钮
            3. 打开购物车验证
        """
        AllureHelper.title("从首页添加商品到购物车")
        AllureHelper.severity("critical")
        AllureHelper.feature("购物车")

        self._login_and_go_home(login_page, home_page, admin_user)
        self._clear_cart(cart_page)

        home_page.open()
        product_name = home_page.get_product_name(0)
        home_page.add_product_to_cart(0)

        cart_page.open()
        assert cart_page.has_item(product_name), \
            f"购物车中应该包含 '{product_name}'"

    @pytest.mark.regression
    @pytest.mark.p1
    def test_add_multiple_products(self, login_page, home_page, product_page, cart_page, admin_user):
        """
        验证添加多个不同商品到购物车

        步骤：
            1. 登录
            2. 添加第一个商品
            3. 返回首页，添加第二个商品
            4. 验证购物车中有两种商品
        """
        AllureHelper.title("添加多个不同商品到购物车")
        AllureHelper.feature("购物车")
        AllureHelper.story("添加商品")

        self._login_and_go_home(login_page, home_page, admin_user)
        self._clear_cart(cart_page)

        home_page.open()

        # 添加第一个商品
        name1 = home_page.get_product_name(0)
        home_page.click_product(0)
        product_page.add_to_cart()

        # 返回首页，添加第二个商品
        home_page.open()
        name2 = home_page.get_product_name(1)
        home_page.click_product(1)
        product_page.add_to_cart()

        # 验证购物车
        cart_page.open()
        assert cart_page.get_item_count() >= 2, \
            f"购物车应该有至少 2 种商品，实际 {cart_page.get_item_count()} 种"
        assert cart_page.has_item(name1), f"缺少商品：{name1}"
        assert cart_page.has_item(name2), f"缺少商品：{name2}"

    # ========================================
    # 删除购物车
    # ========================================

    @pytest.mark.smoke
    @pytest.mark.p1
    def test_delete_product_from_cart(self, login_page, home_page, product_page, cart_page, admin_user):
        """
        验证删除购物车中的商品

        步骤：
            1. 登录，清空购物车
            2. 添加一个商品到购物车
            3. 打开购物车
            4. 删除该商品
            5. 验证购物车为空
        """
        AllureHelper.title("删除购物车商品")
        AllureHelper.feature("购物车")
        AllureHelper.story("删除商品")

        self._login_and_go_home(login_page, home_page, admin_user)
        self._clear_cart(cart_page)

        home_page.open()

        # 先添加一个商品
        home_page.click_product(0)
        product_page.add_to_cart()

        # 打开购物车并删除
        cart_page.open()
        assert not cart_page.is_empty(), "购物车应该有商品"

        cart_page.delete_item(0)
        cart_page.page.wait_for_timeout(500)

        # 验证购物车为空
        assert cart_page.is_empty(), "删除后购物车应该为空"

    # ========================================
    # 空购物车
    # ========================================

    @pytest.mark.regression
    @pytest.mark.p2
    def test_empty_cart_display(self, login_page, home_page, cart_page, admin_user):
        """
        验证空购物车的展示

        步骤：
            1. 登录
            2. 清空购物车
            3. 直接打开购物车
            4. 验证显示空购物车提示
        """
        AllureHelper.title("空购物车展示")
        AllureHelper.feature("购物车")
        AllureHelper.story("空状态")

        self._login_and_go_home(login_page, home_page, admin_user)
        self._clear_cart(cart_page)

        # 此时购物车已清空，直接验证
        assert cart_page.is_empty(), "未添加商品时购物车应该为空"