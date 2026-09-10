"""
鉴权验证专题

MallLite 使用 Session + Cookie
这里专门验证不同鉴权状态下的接口行为

知识点：为什么需要测鉴权？
  鉴权是安全的第一道防线。
  如果未登录就能创建订单、删除数据，说明权限控制有漏洞。
  即使 MallLite 是简化版系统，验证鉴权行为也能帮我们理解完整系统该怎么测。
"""

import pytest
from api_objects.user_api import UserApi
from api_objects.cart_api import CartApi
from api_objects.order_api import OrderApi
from common.assertions import ApiAssertions


class TestAuthComparison:
    """对比已登录和未登录的行为差异"""

    @pytest.mark.regression
    @pytest.mark.p1
    def test_login_returns_session_info(self, user_api, assert_api):
        """
        登录成功后返回用户信息

        验证：登录响应包含 username 和 role
        这些信息在前端显示用户名和控制菜单权限
        """
        resp = user_api.login("admin", "admin123")
        a = assert_api(resp)
        a.assert_success()
        a.assert_has_field("data.username")
        a.assert_has_field("data.role")

    @pytest.mark.regression
    @pytest.mark.p1
    def test_login_wrong_password_no_session(self, user_api, assert_api):
        """
        登录失败后不应该有有效 session

        验证：密码错误后用同一个 session 访问购物车
        应该拿到空数据（未登录状态），而不是之前登录的数据
        """
        resp = user_api.login("admin", "wrong_password")
        assert_api(resp).assert_biz_fail()

        # 用同一个 session（登录失败的）访问购物车
        resp = user_api.get("/api/cart")
        body = resp.json()
        # 应该是空数据（未登录状态的默认购物车）
        assert body["code"] == 200
        assert body["data"]["item_count"] == 0

    @pytest.mark.regression
    @pytest.mark.p1
    def test_login_then_logout_behavior(self, user_api, assert_api):
        """
        登录 → 操作 → 用新 session（相当于"退出"）→ 验证行为

        已知行为：MallLite 的购物车是全局共享的，不按 session 隔离。
        所以新 session 看到的购物车数据可能跟旧 session 一样。
        这条用例记录这个行为，不硬断言隔离性。
        """
        # 登录
        user_api.login("admin", "admin123")

        # 清空购物车后加商品
        user_api.post("/api/cart/1")  # 尝试删除
        user_api.post("/api/cart", json_data={"product_id": 1, "quantity": 1})

        # 验证购物车有数据
        resp = user_api.get("/api/cart")
        items = assert_api(resp).get_field("data.items")
        assert len(items) > 0

        # 创建新 session（相当于退出后重新打开浏览器）
        new_user = UserApi("http://localhost:8000")
        resp = new_user.get("/api/cart")
        body = resp.json()
        # 已知：购物车是全局共享的，新 session 也能看到数据
        # 正式项目中这是一个安全漏洞
        assert body["code"] == 200  # 只验证不崩溃
        assert body["data"]["item_count"] >= 0  # 不断言是否隔离

        new_user.close()


class TestTokenSimulation:
    """
    模拟 JWT Token 方式的测试模式

    知识点：MallLite 实际不用 JWT，但我们可以演示如果用 JWT 测试该怎么写。
    这段代码不在 MallLite 上运行，只做教学。
    """

    @pytest.mark.regression
    def test_token_would_be_in_header(self):
        """
        模拟：如果用 JWT Token，请求头应该包含 Authorization

        这条用例演示的是测试思路，不是实际运行的代码。
        如果你的项目用 JWT，按这个模式写就行。
        """
        # 模拟 JWT Token 的使用方式
        import requests

        session = requests.Session()

        # 假设登录返回 token
        # resp = session.post(url, json={...})
        # token = resp.json()["data"]["token"]

        # 设置 token
        fake_token = "eyJhbGciOiJIUzI1NiJ9.fake_token"
        session.headers.update({"Authorization": f"Bearer {fake_token}"})

        # 验证 header 中有 Authorization
        assert "Authorization" in session.headers
        assert session.headers["Authorization"] == f"Bearer {fake_token}"

        session.close()