"""
端到端链路测试

核心设计思路：
  1. 在一条测试函数内，用变量在步骤之间传递数据
  2. 所有 API 实例共享同一个 session
  3. 每一步都有断言，失败时能精确定位断在哪一步
"""

import pytest
import time
from api_objects.user_api import UserApi
from api_objects.product_api import ProductApi
from api_objects.cart_api import CartApi
from api_objects.order_api import OrderApi
from common.assertions import ApiAssertions
from common.extractor import Extractor


class TestShoppingFlow:
    """完整购物链路"""

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_new_user_full_flow(self):
        """
        新用户完整购物流程

        链路：注册 → 登录 → 搜索 → 查详情 → 加购 → 改数量 → 下单 → 查单

        为什么不用 fixture？
          这条链路模拟的是一个新用户的完整操作，从零开始。
          每一步的输出都是下一步的输入，用变量传递最直观。
          用 fixture 会让逻辑分散在 conftest 和测试文件两处，不容易看清全貌。
        """
        base = "http://localhost:8000"
        a = ApiAssertions

        # ===== 步骤 1：注册 =====
        # 为什么用时间戳做用户名？避免跟已有用户重复
        user_api = UserApi(base)
        username = f"flow_{int(time.time())}"
        resp = user_api.register(username=username, password="FlowTest123")
        a(resp).assert_success()

        # ===== 步骤 2：登录 =====
        # 登录后 session 自动保存 Cookie，后续请求自动携带
        resp = user_api.login(username, "FlowTest123")
        a(resp).assert_success()

        # ===== 步骤 3：搜索商品 =====
        # 关键：创建新的 API 实例后必须共享 session
        product_api = ProductApi(base)
        product_api.session = user_api.session

        resp = product_api.get_products(keyword="iPhone")
        body = a(resp).assert_success().body
        search_items = Extractor.get(body, "data.items")
        assert len(search_items) > 0, "搜索 iPhone 无结果，后续步骤无法继续"

        # 从搜索结果中提取 product_id（链路中的关键数据传递点）
        product_id = search_items[0]["id"]

        # ===== 步骤 4：查看商品详情 =====
        resp = product_api.get_product(product_id)
        detail = a(resp).assert_success().get_field("data")
        assert detail["price"] > 0

        # ===== 步骤 5：加入购物车 =====
        cart_api = CartApi(base)
        cart_api.session = user_api.session

        resp = cart_api.add_to_cart(product_id=product_id, quantity=2)
        a(resp).assert_success()

        # ===== 步骤 6：修改购物车数量 =====
        resp = cart_api.update_quantity(product_id=product_id, quantity=3)
        a(resp).assert_success()

        # 验证修改生效
        resp = cart_api.get_cart()
        items = a(resp).get_field("data.items")
        cart_item = next((i for i in items if i["product_id"] == product_id), None)
        assert cart_item is not None, "购物车中找不到刚添加的商品"
        assert cart_item["quantity"] == 3

        # ===== 步骤 7：创建订单 =====
        order_api = OrderApi(base)
        order_api.session = user_api.session

        resp = order_api.create_order()
        order_no = a(resp).assert_success().get_field("data.order_no")
        assert "ORD" in order_no

        # ===== 步骤 8：查看订单详情 =====
        resp = order_api.get_order(order_no)
        detail = a(resp).assert_success().get_field("data")
        assert detail["order_no"] == order_no
        assert len(detail["items"]) > 0

        # 清理
        user_api.close()
        product_api.close()
        cart_api.close()
        order_api.close()

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_admin_shopping_flow(self, admin_session):
        """
        管理员购物链路（跳过注册和登录）

        设计思路：
          管理员已有账号且已登录（admin_session 提供）
          专注测试购物业务本身：搜索 → 加购 → 下单 → 查单
          比新用户流程更纯粹，排除了注册/登录的干扰
        """
        base = "http://localhost:8000"
        a = ApiAssertions

        product_api = ProductApi(base)
        product_api.session = admin_session
        cart_api = CartApi(base)
        cart_api.session = admin_session
        order_api = OrderApi(base)
        order_api.session = admin_session

        # 清空购物车（避免之前残留数据影响）
        cart_api.clear_cart()

        # 搜索
        resp = product_api.get_products(page_size=1)
        product_id = a(resp).get_field("data.items")[0]["id"]

        # 加购 → 下单
        resp = cart_api.add_to_cart(product_id=product_id, quantity=1)
        a(resp).assert_success()

        resp = order_api.create_order()
        order_no = a(resp).get_field("data.order_no")

        # 查单
        resp = order_api.get_order(order_no)
        a(resp).assert_success()

# ===== 以下是第 11 篇新增的链式 fixture 演示用例 =====


class TestOrderWithFixtures:
    """
    用链式 fixture 简化订单测试

    对比前面的链路测试：
      链路测试：所有步骤写在一条函数里，用变量传数据
      这里：前置步骤由 fixture 完成，用例只关心自己的验证逻辑

    什么时候用哪种？
      想测试完整流程 → 用链路测试（一条函数从头到尾）
      想测试某个接口（但需要前置数据）→ 用 fixture
    """

    @pytest.mark.regression
    @pytest.mark.order
    def test_order_in_list(self, admin_order_api, assert_api, created_order):
        """
        订单在列表中能找到

        created_order fixture 自动完成"加购物车→下单"
        本用例只关心：查列表 → 验证存在
        """
        order_no = created_order

        resp = admin_order_api.get_orders()
        items = assert_api(resp).get_field("data.items")
        order_nos = [o["order_no"] for o in items]
        assert order_no in order_nos

    @pytest.mark.regression
    @pytest.mark.order
    def test_order_detail_fields(self, admin_order_api, assert_api, created_order):
        """
        订单详情包含必要字段

        created_order 负责创建，本用例负责验证
        """
        resp = admin_order_api.get_order(created_order)
        a = assert_api(resp)
        a.assert_success()
        a.assert_has_field("data.order_no")
        a.assert_has_field("data.status")
        a.assert_has_field("data.items")
        a.assert_has_field("data.total_price")

    @pytest.mark.regression
    @pytest.mark.order
    def test_order_list_vs_detail_consistent(self, admin_order_api, assert_api, created_order):
        """
        订单在列表和详情中的 status 一致

        用 created_order 创建订单，然后从两个接口分别获取数据做对比
        """
        order_no = created_order

        # 从列表中找到该订单
        list_resp = admin_order_api.get_orders()
        list_items = assert_api(list_resp).get_field("data.items")
        list_order = next((o for o in list_items if o["order_no"] == order_no), None)
        assert list_order is not None, f"列表中找不到订单 {order_no}"

        # 从详情中获取
        detail_resp = admin_order_api.get_order(order_no)
        detail = assert_api(detail_resp).get_field("data")

        # 对比
        assert list_order["status"] == detail["status"], \
            f"状态不一致：列表='{list_order['status']}', 详情='{detail['status']}'"


class TestProductWithFixtures:
    """用链式 fixture 简化商品测试"""

    @pytest.mark.regression
    @pytest.mark.product
    def test_product_detail_matches_list(self, product_api, assert_api, first_product):
        """
        商品详情和列表中的数据一致

        first_product fixture 从列表中获取第一个商品
        本用例用它的 id 去查详情，对比 name 和 price
        """
        product = first_product
        assert product is not None, "商品列表为空"

        resp = product_api.get_product(product["id"])
        detail = assert_api(resp).get_field("data")

        assert detail["name"] == product["name"]
        assert detail["price"] == product["price"]
