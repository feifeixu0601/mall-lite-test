"""
购物车接口测试（修正版）

关键发现（来自探针）：
  MallLite 的购物车接口不需要登录
  未登录访问购物车：code=200 + 返回空数据 {items:[], total_price:0, ...}
  未登录添加购物车：code=200 + "iPhone 15 Pro 已加入购物车"

  这意味着系统的购物车是按某种默认方式处理未登录用户的
  鉴权测试需要调整策略
"""

import pytest


class TestCartAdd:

    @pytest.mark.smoke
    @pytest.mark.cart
    @pytest.mark.p0
    def test_add_to_cart(self, admin_cart_api, assert_api):
        """
        已登录用户添加商品到购物车
        """
        resp = admin_cart_api.add_to_cart(product_id=1, quantity=2)
        assert_api(resp).assert_success()

    @pytest.mark.smoke
    @pytest.mark.cart
    def test_cart_has_item_after_add(self, admin_cart_api, assert_api):
        """
        添加后购物车有内容

        流程：添加 → 查询 → 验证有商品
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=1)

        resp = admin_cart_api.get_cart()
        a = assert_api(resp)
        a.assert_success()
        a.assert_list_not_empty("data.items")

        items = a.get_field("data.items")
        product_ids = [i["product_id"] for i in items]
        assert 1 in product_ids, "购物车中应该有商品 ID=1"


class TestCartModify:

    @pytest.mark.regression
    @pytest.mark.cart
    def test_update_quantity(self, admin_cart_api, assert_api):
        """
        修改购物车商品数量

        注意：URL 中用 product_id
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=1)

        resp = admin_cart_api.update_quantity(product_id=1, quantity=5)
        assert_api(resp).assert_success()

        # 验证变化
        resp = admin_cart_api.get_cart()
        items = assert_api(resp).get_field("data.items")
        item = next((i for i in items if i["product_id"] == 1), None)
        assert item is not None, "购物车中应该有商品 ID=1"
        assert item["quantity"] == 5, f"数量应为 5，实际 {item['quantity']}"


class TestCartDelete:

    @pytest.mark.regression
    @pytest.mark.cart
    def test_delete_from_cart(self, admin_cart_api, assert_api):
        """
        删除购物车商品

        注意：URL 中用 product_id
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=1)

        resp = admin_cart_api.delete_from_cart(product_id=1)
        assert_api(resp).assert_success()

        # 验证已删除
        resp = admin_cart_api.get_cart()
        items = assert_api(resp).get_field("data.items")
        product_ids = [i["product_id"] for i in items]
        assert 1 not in product_ids, "商品 ID=1 应该已删除"


class TestCartBehavior:
    """
    购物车行为测试

    基于探针发现的实际行为编写
    """

    @pytest.mark.regression
    @pytest.mark.cart
    def test_cart_empty_default(self, cart_api, assert_api):
        """
        新 session（未登录）访问购物车

        探针确认：返回 code=200 + 空数据
        data = {items:[], total_price:0, total_quantity:0, item_count:0}
        """
        resp = cart_api.get_cart()
        a = assert_api(resp)
        a.assert_success()

        data = a.get_data()
        assert data["item_count"] == 0, "新 session 购物车应该为空"
        assert data["total_price"] == 0
        assert len(data["items"]) == 0

    @pytest.mark.regression
    @pytest.mark.cart
    def test_cart_add_then_check_count(self, admin_cart_api, assert_api):
        """
        添加商品后购物车数量变化

        流程：添加 2 个 → 验证 item_count 变化
        """
        # 记录添加前的数量
        resp = admin_cart_api.get_cart()
        count_before = assert_api(resp).get_field("data.item_count")

        # 添加商品
        admin_cart_api.add_to_cart(product_id=1, quantity=3)

        # 验证数量变化
        resp = admin_cart_api.get_cart()
        count_after = assert_api(resp).get_field("data.item_count")
        assert count_after > count_before, \
            f"添加后数量应增加，添加前={count_before}，添加后={count_after}"

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.negative
    def test_add_invalid_product(self, admin_cart_api, assert_api):
        """添加不存在的商品到购物车"""
        resp = admin_cart_api.add_to_cart(product_id=99999, quantity=1)
        assert_api(resp).assert_biz_fail()