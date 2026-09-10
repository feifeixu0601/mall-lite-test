"""
接口自动化 - conftest.py（增强版）

增强点：
1. 登录 session 改为 session scope，整个会话只登录一次
2. 每个用例执行前自动清空购物车，避免数据污染
3. 新增 admin_user_api fixture
"""

import pytest
from api_objects.user_api import UserApi
from api_objects.product_api import ProductApi
from api_objects.cart_api import CartApi
from api_objects.order_api import OrderApi
from common.assertions import ApiAssertions
from common.logger import get_logger

logger = get_logger("conftest")

BASE_URL = "http://localhost:8000"


# ========================================
# session 级共享（只登录一次）
# ========================================

@pytest.fixture(scope="session")
def admin_session():
    """
    管理员登录后的 session（整个测试会话只创建一次）

    原理：
      UserApi 登录后 session 保存了 Cookie
      所有需要登录的 fixture 共享这个 session
      不需要重复登录，节省大量时间
    """
    user = UserApi(BASE_URL)
    session = user.login_and_share("admin", "admin123")
    return session


# ========================================
# 未登录的 API 客户端
# ========================================

@pytest.fixture
def user_api():
    """用户 API（未登录）"""
    api = UserApi(BASE_URL)
    yield api
    api.close()


@pytest.fixture
def product_api():
    """商品 API（不需要登录）"""
    api = ProductApi(BASE_URL)
    yield api
    api.close()


@pytest.fixture
def cart_api():
    """购物车 API（未登录）"""
    api = CartApi(BASE_URL)
    yield api
    api.close()


@pytest.fixture
def order_api():
    """订单 API（未登录）"""
    api = OrderApi(BASE_URL)
    yield api
    api.close()


# ========================================
# 已登录的 API 客户端（共享 session）
# ========================================

@pytest.fixture
def admin_user_api(admin_session):
    """已登录的用户 API"""
    api = UserApi(BASE_URL)
    api.session = admin_session
    return api


@pytest.fixture
def admin_cart_api(admin_session):
    """已登录的购物车 API"""
    api = CartApi(BASE_URL)
    api.session = admin_session
    return api


@pytest.fixture
def admin_order_api(admin_session):
    """已登录的订单 API"""
    api = OrderApi(BASE_URL)
    api.session = admin_session
    return api


# ========================================
# 自动清理（避免用例间数据污染）
# ========================================
"""
@pytest.fixture(autouse=True)
def clean_cart(admin_session):
    
    每个用例执行前自动清空购物车
    为什么需要这个？
      因为 admin_session 是共享的，用例 A 往购物车加了商品，
      用例 B 执行时购物车不是空的，会导致用例 B 的断言失败。
      通过 autouse=True 自动清理，每个用例开始时购物车都是空的。
  
    cart = CartApi(BASE_URL)
    cart.session = admin_session
    cart.clear_cart()
    yield
    
  """

# ========================================
# 工具和数据
# ========================================

@pytest.fixture
def assert_api():
    """断言工具"""
    return ApiAssertions


# ===== 以下是第 11 篇新增的链式 fixture =====

@pytest.fixture
def created_order(admin_cart_api, admin_order_api):
    """
    链式 fixture：先创建一个订单，返回 order_no

    依赖链：
      admin_session → admin_cart_api + admin_order_api（共享 session）
                         ↓
                    加购物车 → 创建订单
                         ↓
                    返回 order_no

    使用者只需要接收 order_no，不用关心前置步骤
    """
    admin_cart_api.clear_cart()
    admin_cart_api.add_to_cart(product_id=1, quantity=1)
    resp = admin_order_api.create_order()
    order_no = resp.json()["data"]["order_no"]
    return order_no


@pytest.fixture
def first_product(product_api):
    """
    链式 fixture：获取商品列表中第一个商品的完整信息

    使用者拿到 {"id": ..., "name": ..., "price": ...} 后
    可以直接用来做各种商品相关测试
    """
    resp = product_api.get_products(page_size=1)
    items = resp.json()["data"]["items"]
    return items[0] if items else None

@pytest.fixture
def admin_account():
    return {"username": "admin", "password": "admin123"}
# ===== 数据清理策略 =====

@pytest.fixture(autouse=True)
def clean_cart(admin_session):
    """
    策略 1：前置清理

    autouse=True 表示自动对所有用例生效。
    每个用例开始前自动清空购物车，避免上一个用例残留的数据影响当前用例。

    适用场景：购物车这种会被频繁修改的数据
    """
    cart = CartApi(BASE_URL)
    cart.session = admin_session
    cart.clear_cart()
    yield  # 用例执行


@pytest.fixture
def unique_username():
    """
    策略 3：独立数据

    用时间戳生成唯一用户名，每个用例注册不同的账号。
    不需要清理，因为每个账号只用一次。

    适用场景：注册接口测试
    """
    return f"test_{int(time.time() * 1000)}"


# 以下是策略 2 的示例（不在 MallLite 上运行，做教学演示）：
#
# @pytest.fixture
# def created_and_cleanup(admin_cart_api, admin_order_api):
#     """
#     策略 2：后置清理
#
#     yield 之前是 setup（创建数据）
#     yield 之后是 teardown（清理数据）
#
#     适用场景：创建了不可逆的数据（如订单），需要在用例结束后清理
#     """
#     admin_cart_api.add_to_cart(product_id=1, quantity=1)
#     resp = admin_order_api.create_order()
#     order_no = resp.json()["data"]["order_no"]
#
#     yield order_no  # 用例执行，把 order_no 传给用例
#
#     # 用例结束后清理（如果 MallLite 有删除订单的接口）
#     # admin_order_api.delete_order(order_no)

import allure

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Allure Hook：自动附加请求/响应日志到报告

    知识点：hookwrapper 是什么？
      Pytest 的 hook 机制允许你在测试执行的各个阶段插入自定义逻辑。
      hookwrapper 会在用例执行完成后触发。
      我们在这里捕获失败的用例，把请求/响应信息附加到 Allure 报告中。
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # 用例执行失败时，附加额外信息到报告
        # 这些信息会在 Allure 报告的"附件"区域显示
        try:
            allure.attach(
                name="测试失败信息",
                body=str(report.longrepr),
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            pass
