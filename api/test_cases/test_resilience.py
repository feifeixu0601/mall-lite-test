"""
超时和重试验证

验证第 10 篇在 ApiClient 中实现的重试机制和容错能力
"""

import pytest
import requests
from api_objects.base_api import ApiClient
from common.assertions import ApiAssertions


class TestTimeout:
    """超时验证"""

    @pytest.mark.regression
    @pytest.mark.p2
    def test_request_timeout_error(self):
        """
        极短超时触发 Timeout 异常

        已知：在 Windows + localhost 环境下，timeout=0.001 可能不会触发超时，
        因为 localhost 的 TCP 连接是内存级别的，速度极快。
        在远程服务器或 CI/CD 环境中，这个测试会正常触发 Timeout。

        如果当前环境没触发，标记为 xfail（已知平台限制）。
        """
        session = requests.Session()
        try:
            with pytest.raises(requests.exceptions.Timeout):
                session.get("http://localhost:8000/api/products", timeout=0.001)
        except pytest.fail.Exception:
            # DID NOT RAISE — localhost 太快，timeout 没生效
            pytest.xfail("Windows + localhost 环境下极短 timeout 不可靠")
        finally:
            session.close()

    @pytest.mark.regression
    @pytest.mark.p2
    def test_normal_request_no_timeout(self, product_api, assert_api):
        """正常请求不超时"""
        resp = product_api.get_products()
        assert_api(resp).assert_success()

    @pytest.mark.regression
    @pytest.mark.p2
    def test_timeout_via_base_api(self):
        """
        通过 ApiClient 发送带超时的请求

        同 test_request_timeout_error，localhost 上可能不触发
        """
        api = ApiClient("http://localhost:8000")
        try:
            with pytest.raises(requests.exceptions.Timeout):
                api.get("/api/products", timeout=0.001)
        except pytest.fail.Exception:
            pytest.xfail("Windows + localhost 环境下极短 timeout 不可靠")
        finally:
            api.close()

    @pytest.mark.regression
    @pytest.mark.p2
    def test_connection_error(self):
        """
        连接不存在的服务器触发 ConnectionError

        日志显示 Retry 会重试 2 次，共等约 15 秒后才报错
        这恰好证明重试机制在工作
        """
        api = ApiClient("http://localhost:19999")
        with pytest.raises(requests.exceptions.ConnectionError):
            api.get("/api/products")
        api.close()

    @pytest.mark.regression
    @pytest.mark.p2
    def test_invalid_url_returns_error(self):
        """请求不存在的路径，返回 404"""
        api = ApiClient("http://localhost:8000")
        resp = api.get("/api/nonexistent_path_xyz")
        assert resp.status_code in (404, 405, 500)
        api.close()


class TestRetryStrategy:
    """
    重试策略验证

    第 10 篇配置了：GET/PUT/DELETE 对 5xx 自动重试 2 次
    POST 不重试，避免重复创建资源
    """

    @pytest.mark.regression
    @pytest.mark.p2
    def test_retry_config_is_applied(self):
        """
        验证重试配置已生效

        检查 session 的 adapter 中 Retry 的参数
        这不是测试 MallLite，而是测试我们自己的框架配置
        """
        api = ApiClient("http://localhost:8000")

        adapter = api.session.get_adapter("http://localhost:8000")
        retry = adapter.max_retries

        assert retry.total == 2, f"重试次数期望 2，实际 {retry.total}"
        assert 500 in retry.status_forcelist
        assert 502 in retry.status_forcelist
        assert 503 in retry.status_forcelist
        assert 504 in retry.status_forcelist

        api.close()

    @pytest.mark.regression
    @pytest.mark.p2
    def test_post_not_in_retry_list(self):
        """
        POST 不在重试列表中

        POST 创建资源，重试会重复创建
        """
        api = ApiClient("http://localhost:8000")

        adapter = api.session.get_adapter("http://localhost:8000")
        retry = adapter.max_retries

        if retry.allowed_methods is not None:
            assert "POST" not in retry.allowed_methods, \
                "POST 不应该在重试列表中"

        api.close()

    @pytest.mark.regression
    @pytest.mark.p2
    def test_request_statistics(self):
        """
        验证请求统计功能

        _request_count 记录总请求数，_fail_count 记录失败数
        """
        api = ApiClient("http://localhost:8000")

        assert api._request_count == 0
        assert api._fail_count == 0

        # 3 次正常请求
        api.get("/api/products")
        api.get("/api/products")
        api.get("/api/products")

        assert api._request_count == 3
        assert api._fail_count == 0

        # 1 次失败请求（404）
        api.get("/api/nonexistent")

        assert api._request_count == 4
        assert api._fail_count == 1

        api.close()

    @pytest.mark.regression
    @pytest.mark.p2
    def test_multiple_requests_stable(self):
        """
        连续多次请求都正常

        验证 session 稳定性
        """
        api = ApiClient("http://localhost:8000")

        for i in range(5):
            resp = api.get("/api/products")
            assert resp.status_code == 200, f"第 {i+1} 次请求失败"

        assert api._request_count == 5
        assert api._fail_count == 0

        api.close()


class TestConcurrency:
    """
    并发场景测试

    用 threading 模拟多用户同时操作
    """

    @pytest.mark.regression
    @pytest.mark.p2
    def test_concurrent_login(self):
        """
        多个线程同时登录同一个账号

        验证：不会因为并发登录导致错误
        """
        import threading

        base = "http://localhost:8000"
        results = []

        def login_account():
            try:
                user = ApiClient(base)
                resp = user.post("/api/login", json_data={
                    "username": "admin", "password": "admin123"
                })
                results.append(("success", resp.json()["code"]))
                user.close()
            except Exception as e:
                results.append(("error", str(e)))

        threads = [threading.Thread(target=login_account) for _ in range(3)]

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert len(results) == 3
        for status, code in results:
            assert status == "success", f"有线程报错：{results}"
            assert code == 200

    @pytest.mark.regression
    @pytest.mark.p2
    def test_concurrent_get_products(self):
        """
        多个线程同时查询商品列表

        验证：并发读取不会导致错误
        """
        import threading

        base = "http://localhost:8000"
        results = []

        def get_products():
            try:
                api = ApiClient(base)
                resp = api.get("/api/products")
                results.append(("success", resp.status_code))
                api.close()
            except Exception as e:
                results.append(("error", str(e)))

        threads = [threading.Thread(target=get_products) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert len(results) == 5
        for status, code in results:
            assert status == "success", f"有线程报错：{results}"
            assert code == 200

# ===== 以下是并发测试 =====

import threading
import time
from api_objects.user_api import UserApi
from api_objects.cart_api import CartApi
from api_objects.order_api import OrderApi


class TestConcurrency:
    """
    并发场景测试

    用 Python 的 threading 模块模拟多用户同时操作

    知识点：threading 的作用
      每个线程模拟一个用户的操作。
      多个线程同时启动，模拟"同一时刻"多个请求并发到达服务端。
    """

    @pytest.mark.regression
    @pytest.mark.p2
    def test_concurrent_add_to_cart(self):
        """
        两个线程同时加同一件商品到购物车

        验证：两个请求都成功，购物车最终状态正确
        """
        base = "http://localhost:8000"
        results = []

        def add_cart(username, password):
            """每个线程的执行函数"""
            try:
                user = UserApi(base)
                user.login(username, password)
                cart = CartApi(base)
                cart.session = user.session
                cart.clear_cart()
                resp = cart.add_to_cart(product_id=1, quantity=1)
                results.append(("success", resp.json()["code"]))
                user.close()
            except Exception as e:
                results.append(("error", str(e)))

        # 创建两个线程，同时启动
        t1 = threading.Thread(target=add_cart, args=("admin", "admin123"))
        t2 = threading.Thread(target=add_cart, args=("testuser", "test123"))

        t1.start()
        t2.start()

        # 等待两个线程都完成
        t1.join(timeout=30)
        t2.join(timeout=30)

        # 两个都应该成功
        assert len(results) == 2, f"期望 2 个结果，实际 {len(results)}"
        for status, code in results:
            assert status == "success", f"有线程报错：{results}"
            assert code == 200, f"有请求失败：code={code}"

    @pytest.mark.regression
    @pytest.mark.p2
    def test_concurrent_login(self):
        """
        多个线程同时登录同一个账号

        验证：不会因为并发登录导致错误
        """
        base = "http://localhost:8000"
        results = []

        def login_account():
            try:
                user = UserApi(base)
                resp = user.login("admin", "admin123")
                results.append(resp.json()["code"])
                user.close()
            except Exception as e:
                results.append(str(e))

        threads = []
        for _ in range(3):
            t = threading.Thread(target=login_account)
            threads.append(t)

        # 同时启动 3 个线程
        for t in threads:
            t.start()

        # 等待全部完成
        for t in threads:
            t.join(timeout=30)

        # 都应该成功
        assert len(results) == 3
        for code in results:
            assert code == 200, f"并发登录失败：{results}"

    @pytest.mark.regression
    @pytest.mark.p2
    def test_concurrent_create_order(self):
        """
        两个线程同时创建订单

        验证：不会因为并发下单导致错误
        """
        base = "http://localhost:8000"
        results = []

        def create_order():
            try:
                user = UserApi(base)
                user.login("admin", "admin123")
                cart = CartApi(base)
                cart.session = user.session
                cart.clear_cart()
                cart.add_to_cart(product_id=1, quantity=1)

                order = OrderApi(base)
                order.session = user.session
                resp = order.create_order()
                results.append(("success", resp.json()["code"]))
                user.close()
            except Exception as e:
                results.append(("error", str(e)))

        t1 = threading.Thread(target=create_order)
        t2 = threading.Thread(target=create_order)

        t1.start()
        t2.start()

        t1.join(timeout=30)
        t2.join(timeout=30)

        assert len(results) == 2
        for status, code in results:
            assert status == "success", f"有线程报错：{results}"
