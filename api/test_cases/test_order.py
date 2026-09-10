"""
订单接口测试
"""

import pytest


class TestOrderCreate:

    @pytest.mark.smoke
    @pytest.mark.order
    @pytest.mark.p0
    def test_create_order(self, admin_cart_api, admin_order_api, assert_api):
        """创建订单"""
        admin_cart_api.add_to_cart(product_id=1, quantity=1)

        resp = admin_order_api.create_order()
        a = assert_api(resp)
        a.assert_success()
        a.assert_has_field("data.order_no")
        assert "ORD" in a.get_field("data.order_no")

    @pytest.mark.regression
    @pytest.mark.order
    @pytest.mark.negative
    def test_create_order_empty_cart(self, admin_order_api, assert_api):
        """空购物车不能创建订单（探针确认：code=400, message=购物车为空）"""
        resp = admin_order_api.create_order()
        a = assert_api(resp)
        a.assert_biz_fail()
        a.assert_code(400)
        a.assert_message("购物车为空")


class TestOrderQuery:

    @pytest.mark.smoke
    @pytest.mark.order
    def test_order_in_list(self, admin_cart_api, admin_order_api, assert_api):
        """创建的订单在列表中能找到"""
        admin_cart_api.add_to_cart(product_id=1, quantity=1)
        create_resp = admin_order_api.create_order()
        order_no = assert_api(create_resp).get_field("data.order_no")

        resp = admin_order_api.get_orders()
        a = assert_api(resp)
        a.assert_success()

        order_nos = [o["order_no"] for o in a.get_field("data.items")]
        assert order_no in order_nos, f"订单 {order_no} 不在列表中"

    @pytest.mark.smoke
    @pytest.mark.order
    def test_order_detail(self, admin_cart_api, admin_order_api, assert_api):
        """
        获取订单详情

        确认：用 order_no 查详情，不是 id
        确认：返回字段有 order_no、user_id、items、total_price、status、created_at
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=1)
        create_resp = admin_order_api.create_order()
        order_no = assert_api(create_resp).get_field("data.order_no")

        # 直接用 order_no 查详情
        resp = admin_order_api.get_order(order_no)
        a = assert_api(resp)
        a.assert_success()
        a.assert_field_value("data.order_no", order_no)
        a.assert_has_field("data.status")
        a.assert_has_field("data.total_price")
        a.assert_has_field("data.items")

    @pytest.mark.regression
    @pytest.mark.order
    def test_order_detail_after_create(self, admin_cart_api, admin_order_api, assert_api):
        """创建订单后详情中包含商品信息"""
        admin_cart_api.add_to_cart(product_id=1, quantity=2)

        create_resp = admin_order_api.create_order()
        order_no = assert_api(create_resp).get_field("data.order_no")

        resp = admin_order_api.get_order(order_no)
        a = assert_api(resp)
        a.assert_success()
        a.assert_has_field("data.items")

        items = a.get_field("data.items")
        assert len(items) > 0
        # 验证商品信息完整
        assert "name" in items[0]
        assert "price" in items[0]
        assert "quantity" in items[0]


class TestOrderBehavior:

    @pytest.mark.regression
    @pytest.mark.order
    def test_order_list_default(self, order_api):
        """未登录也能查看订单列表（探针确认）"""
        resp = order_api.get_orders()
        body = resp.json()
        assert body["code"] == 200
        assert "items" in body["data"]