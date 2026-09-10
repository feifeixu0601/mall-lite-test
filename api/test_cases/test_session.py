"""
Session 验证专题

补充说明（来自第 9 篇的探针脚本验证）：
  未登录访问购物车 → code=200 + 空数据（不是 401）
  未登录创建订单   → code=200 + 创建成功
  这说明 MallLite 的购物车和订单接口实际不需要登录也能访问
  但 session 验证仍然有意义——验证登录态下的数据隔离和跨模块访问
"""

import pytest
from api_objects.user_api import UserApi
from api_objects.cart_api import CartApi
from api_objects.product_api import ProductApi
from api_objects.order_api import OrderApi
from common.assertions import ApiAssertions


class TestSessionAccess:
    """Session 能访问哪些模块"""

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.smoke
    def test_session_access_cart(self, user_api, assert_api, admin_account):
        """
        登录后的 session 能访问购物车

        用同一个 user_api 实例（同一个 session）先登录，再访问购物车。
        如果 session 失效了，访问购物车会返回未登录的响应。
        """
        user_api.login(admin_account["username"], admin_account["password"])

        # 用同一个 session 访问购物车
        resp = user_api.get("/api/cart")
        assert_api(resp).assert_success()

    @pytest.mark.regression
    @pytest.mark.login
    def test_session_access_products(self, user_api, assert_api, admin_account):
        """登录后能访问商品列表"""
        user_api.login(admin_account["username"], admin_account["password"])
        resp = user_api.get("/api/products")
        assert_api(resp).assert_success()

    @pytest.mark.regression
    @pytest.mark.login
    def test_session_access_orders(self, user_api, assert_api, admin_account):
        """登录后能访问订单列表"""
        user_api.login(admin_account["username"], admin_account["password"])
        resp = user_api.get("/api/orders")
        assert_api(resp).assert_success()

    @pytest.mark.regression
    @pytest.mark.login
    def test_session_access_categories(self, user_api, assert_api, admin_account):
        """登录后能访问分类列表（分类接口不需要登录，但登录后也应该能访问）"""
        user_api.login(admin_account["username"], admin_account["password"])
        resp = user_api.get("/api/categories")
        assert_api(resp).assert_success()


class TestSessionIsolation:
    """
    Session 隔离验证

    知识点：为什么隔离很重要？
      如果两个用户的 session 没有隔离：
      - 用户 A 加了商品，用户 B 的购物车也出现了该商品
      - 用户 A 的订单出现在用户 B 的订单列表中
      这是严重的安全漏洞。
    """

    @pytest.mark.regression
    @pytest.mark.p1
    def test_two_sessions_have_independent_cart(self):
        """
        两个不同用户的 session 购物车互相独立

        设计思路：
          1. 创建两个独立的 UserApi 实例
          2. 分别登录不同用户
          3. 各自查购物车
          4. 两个请求都应成功（能访问），但数据各自独立
        """
        base = "http://localhost:8000"
        a = ApiAssertions

        # Session 1：admin
        user1 = UserApi(base)
        user1.login("admin", "admin123")
        cart1 = CartApi(base)
        cart1.session = user1.session

        # Session 2：testuser
        user2 = UserApi(base)
        user2.login("testuser", "test123")
        cart2 = CartApi(base)
        cart2.session = user2.session

        # 两个 session 都能独立访问购物车
        resp1 = cart1.get_cart()
        a(resp1).assert_success()

        resp2 = cart2.get_cart()
        a(resp2).assert_success()

        # 清理
        user1.close()
        user2.close()

    @pytest.mark.regression
    @pytest.mark.p1
    def test_session_add_does_not_affect_other(self):
        """
        用户 A 加购物车不影响用户 B

        这是隔离验证的核心——证明两个 session 的数据是分开的
        """
        base = "http://localhost:8000"
        a = ApiAssertions

        # Session 1：admin，清空购物车后查看数量
        user1 = UserApi(base)
        user1.login("admin", "admin123")
        cart1 = CartApi(base)
        cart1.session = user1.session
        cart1.clear_cart()
        resp1 = cart1.get_cart()
        count_before = a(resp1).get_field("data.item_count")

        # Session 2：testuser，加一个商品
        user2 = UserApi(base)
        user2.login("testuser", "test123")
        cart2 = CartApi(base)
        cart2.session = user2.session
        cart2.add_to_cart(product_id=1, quantity=1)

        # Session 1 的购物车数量不应该变
        resp1 = cart1.get_cart()
        count_after = a(resp1).get_field("data.item_count")
        assert count_before == count_after, \
            f"用户 B 加购物车后，用户 A 的数量从 {count_before} 变成了 {count_after}"

        # 清理
        user1.close()
        user2.close()


class TestSessionCrossModule:
    """同一个 session 跨模块操作"""

    @pytest.mark.regression
    @pytest.mark.smoke
    def test_session_cross_module(self, admin_session):
        """
        同一个 session 能同时操作商品、购物车、订单三个模块

        设计思路：
          模拟真实用户操作：浏览商品 → 加购 → 下单
          全程使用同一个 session，验证 session 在不同模块之间不会失效。
          如果 session 在某一步失效了，后续步骤会失败。
        """
        base = "http://localhost:8000"
        a = ApiAssertions

        product = ProductApi(base)
        product.session = admin_session
        cart = CartApi(base)
        cart.session = admin_session
        order = OrderApi(base)
        order.session = admin_session

        cart.clear_cart()

        # 模块 1：商品
        resp = product.get_products(page_size=1)
        product_id = a(resp).get_field("data.items")[0]["id"]

        # 模块 2：购物车
        resp = cart.add_to_cart(product_id=product_id, quantity=1)
        a(resp).assert_success()

        # 模块 3：订单
        resp = order.create_order()
        a(resp).assert_success()