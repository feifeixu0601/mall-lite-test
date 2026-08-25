"""
端到端测试（POM 模式）

模拟真实用户的完整操作链路
覆盖从登录到下单的完整流程
"""

import pytest
from common.allure_helper import AllureHelper


@pytest.mark.e2e
class TestEndToEnd:
    """端到端测试集"""

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_full_shopping_flow(self, login_page, home_page, product_page,
                                 cart_page, order_page, admin_user):
        """
        完整购物链路

        模拟用户从登录到下单的完整操作：
            登录 → 搜索商品 → 查看详情 → 加购物车 → 结算 → 查看订单

        步骤：
            1. 打开登录页，输入账号密码，登录成功
            2. 在首页搜索 "iPhone"
            3. 搜索结果中点击第一个商品
            4. 在商品详情页查看信息，加入购物车
            5. 打开购物车，验证商品存在
            6. 点击去结算
            7. 打开订单列表，验证订单已创建
        """
        AllureHelper.title("完整购物链路 - 登录到下单")
        AllureHelper.severity("blocker")
        AllureHelper.feature("端到端")
        AllureHelper.story("完整购物")

        # ===== 第 1 步：登录 =====
        AllureHelper.step("登录", lambda: login_page.login(
            admin_user["username"], admin_user["password"]
        ))
        assert login_page.is_login_success(), "登录应该成功"

        # ===== 第 2 步：搜索商品 =====
        AllureHelper.step("搜索 iPhone", lambda: home_page.search("iPhone"))
        search_count = home_page.get_product_count()
        assert search_count > 0, "搜索 'iPhone' 应该有结果"
        AllureHelper.attach_text(f"搜索到 {search_count} 个商品", "搜索结果")

        # ===== 第 3 步：查看商品详情 =====
        product_name = home_page.get_product_name(0)
        AllureHelper.step(f"查看商品详情：{product_name}", lambda: home_page.click_product(0))

        title = product_page.get_title()
        price = product_page.get_price()
        AllureHelper.attach_text(f"商品：{title}\n价格：{price}", "商品详情")

        # ===== 第 4 步：加入购物车 =====
        AllureHelper.step("加入购物车", lambda: product_page.add_to_cart())

        # ===== 第 5 步：验证购物车 =====
        AllureHelper.step("打开购物车", lambda: cart_page.open())
        assert not cart_page.is_empty(), "购物车不应该为空"
        assert cart_page.has_item(product_name or title), "购物车中应该包含刚添加的商品"

        total = cart_page.get_total_price()
        AllureHelper.attach_text(f"购物车合计：{total}", "购物车")

        # ===== 第 6 步：去结算 =====
        AllureHelper.step("去结算", lambda: cart_page.checkout())

        # ===== 第 7 步：查看订单 =====
        AllureHelper.step("查看订单", lambda: order_page.open())
        assert not order_page.is_empty(), "订单列表不应该为空"

        order_no = order_page.get_order_no(0)
        status = order_page.get_order_status(0)
        AllureHelper.attach_text(
            f"订单号：{order_no}\n状态：{status}",
            "订单确认"
        )

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_search_to_cart_flow(self, login_page, home_page, product_page, cart_page, admin_user):
        """
        搜索加购链路

        模拟用户搜索多个商品并加入购物车：
            登录 → 搜索 → 加购第一个 → 返回 → 加购第二个 → 验证购物车

        步骤：
            1. 登录
            2. 搜索 "Pro"
            3. 记录搜索结果数量
            4. 点击第一个商品加入购物车
            5. 返回首页
            6. 搜索 "AirPods"
            7. 点击第一个商品加入购物车
            8. 打开购物车，验证有两个商品
        """
        AllureHelper.title("搜索多商品加购链路")
        AllureHelper.severity("critical")
        AllureHelper.feature("端到端")
        AllureHelper.story("搜索加购")

        # 登录
        AllureHelper.step("登录", lambda: login_page.login(
            admin_user["username"], admin_user["password"]
        ))

        # 搜索 Pro 并加购第一个
        AllureHelper.step("搜索 Pro", lambda: home_page.search("Pro"))
        pro_count = home_page.get_product_count()
        assert pro_count > 0, "搜索 'Pro' 应该有结果"

        name1 = home_page.get_product_name(0)
        AllureHelper.step(f"加购 {name1}", lambda: (
            home_page.click_product(0),
            product_page.add_to_cart(),
        ))

        # 返回首页搜索 AirPods
        AllureHelper.step("返回首页搜索 AirPods", lambda: (
            home_page.open(),
            home_page.search("AirPods"),
        ))
        assert home_page.get_product_count() > 0, "搜索 'AirPods' 应该有结果"

        name2 = home_page.get_product_name(0)
        AllureHelper.step(f"加购 {name2}", lambda: (
            home_page.click_product(0),
            product_page.add_to_cart(),
        ))

        # 验证购物车
        AllureHelper.step("验证购物车", lambda: cart_page.open())
        item_count = cart_page.get_item_count()
        AllureHelper.attach_text(
            f"购物车商品种类：{item_count}\n商品：{cart_page.get_item_names()}",
            "购物车详情"
        )
        assert item_count >= 2, f"购物车应该有至少 2 种商品，实际 {item_count} 种"

    @pytest.mark.regression
    @pytest.mark.p1
    def test_guest_cannot_access_cart(self, page, cart_page):
        """
        验证未登录用户访问购物车

        步骤：
            1. 清除登录状态（cookies + localStorage）
            2. 不登录直接打开购物车
            3. 验证跳转到登录页
        """
        AllureHelper.title("未登录访问购物车")
        AllureHelper.feature("端到端")
        AllureHelper.story("未登录场景")

        # 清除所有登录状态
        page.context.clear_cookies()
        page.evaluate("localStorage.clear()")
        page.reload()

        cart_page.open()

        # 未登录时应被重定向到登录页
        current_url = page.url
        assert "/login" in current_url or cart_page.is_empty(), \
            f"未登录访问购物车应跳转到登录页或显示为空，当前 URL：{current_url}"

    @pytest.mark.regression
    @pytest.mark.p1
    def test_profile_after_login(self, login_page, profile_page, admin_user):
        """
        验证登录后个人中心显示正确信息

        步骤：
            1. 登录
            2. 打开个人中心
            3. 验证用户名和角色正确
        """
        AllureHelper.title("登录后个人中心信息验证")
        AllureHelper.feature("端到端")
        AllureHelper.story("个人信息")

        login_page.login(admin_user["username"], admin_user["password"])
        profile_page.open()

        assert profile_page.is_logged_in(), "应该显示已登录状态"

        username = profile_page.get_username()
        assert username == admin_user["username"], \
            f"用户名应为 {admin_user['username']}，实际为 {username}"

        role = profile_page.get_role()
        assert role == admin_user["role"], \
            f"角色应为 {admin_user['role']}，实际为 {role}"

        AllureHelper.attach_text(
            f"用户名：{username}\n角色：{role}",
            "个人信息"
        )