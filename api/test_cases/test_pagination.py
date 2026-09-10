"""
分页测试

覆盖四个关注点：
  1. 基本分页：翻页后数据不同
  2. page_size 限制：返回数量不超过 page_size
  3. 数据唯一性：同一条数据不会出现在不同页
  4. 参数边界：不合理参数不导致崩溃
"""

import pytest


class TestProductPagination:
    """商品列表分页"""

    @pytest.mark.regression
    @pytest.mark.product
    def test_page1_and_page2_different(self, product_api, assert_api):
        """
        第 1 页和第 2 页的数据不重复

        这是分页最基本的要求——翻页后看到的是新数据
        """
        resp1 = product_api.get_products(page=1, page_size=3)
        resp2 = product_api.get_products(page=2, page_size=3)

        items1 = assert_api(resp1).get_field("data.items")
        items2 = assert_api(resp2).get_field("data.items")

        # 两边都有数据时才比较
        if len(items1) > 0 and len(items2) > 0:
            ids1 = {i["id"] for i in items1}
            ids2 = {i["id"] for i in items2}
            # isdisjoint() 判断两个集合有没有交集
            assert ids1.isdisjoint(ids2), \
                f"第 1 页和第 2 页有重复数据：{ids1 & ids2}"

    @pytest.mark.regression
    @pytest.mark.product
    def test_page_size_limits_results(self, product_api, assert_api):
        """
        page_size 限制返回数量

        page_size=1 最多返回 1 条
        page_size=5 最多返回 5 条
        """
        resp1 = product_api.get_products(page=1, page_size=1)
        resp5 = product_api.get_products(page=1, page_size=5)

        items1 = assert_api(resp1).get_field("data.items")
        items5 = assert_api(resp5).get_field("data.items")

        assert len(items1) <= 1, f"page_size=1 但返回了 {len(items1)} 条"
        assert len(items5) <= 5, f"page_size=5 但返回了 {len(items5)} 条"
        assert len(items5) >= len(items1)

    @pytest.mark.regression
    @pytest.mark.product
    def test_page3_may_have_data(self, product_api):
        """
        第 3 页数据（如果足够多）

        不做硬性断言——如果商品少于 6 条，第 3 页可以为空。
        这里只验证接口能正常响应。
        """
        resp = product_api.get_products(page=3, page_size=2)
        body = resp.json()
        assert body["code"] == 200

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.negative
    @pytest.mark.parametrize("page,page_size,desc", [
        (0, 10, "page=0"),
        (-1, 10, "page=-1（负数页码）"),
        (1, 0, "page_size=0"),
        (1, -1, "page_size=-1（负数大小）"),
        (1, 10000, "page_size=10000（极大值）"),
        (9999, 10, "page=9999（超出范围）"),
    ], ids=["page=0", "page=-1", "size=0", "size=-1", "size极大", "page极大"])
    def test_pagination_boundary(self, product_api, page, page_size, desc):
        """
        分页参数边界值

        知识点：ids=lambda x: x[2]
          parametrize 的 ids 参数控制用例名的显示方式。
          lambda x: x[2] 表示用参数元组的第三个元素（desc）做名字。
          这样用例名会显示为 test_pagination_boundary[page=0] 而不是 test_pagination_boundary[0-10-xxx]
        """
        resp = product_api.get_products(page=page, page_size=page_size)
        # 最基本的要求：不崩溃（不是 HTTP 500）
        assert resp.status_code == 200, \
            f"{desc} 导致 HTTP {resp.status_code}"


class TestOrderPagination:
    """订单列表分页"""

    @pytest.mark.regression
    @pytest.mark.order
    def test_order_list_has_data(self, admin_order_api, assert_api, created_order):
        """
        订单列表至少有数据

        用 created_order fixture 保证至少有一个订单
        """
        resp = admin_order_api.get_orders()
        a = assert_api(resp)
        a.assert_success()
        a.assert_list_not_empty("data.items")

    @pytest.mark.regression
    @pytest.mark.order
    @pytest.mark.negative
    @pytest.mark.parametrize("page,page_size", [
        (0, 10),
        (-1, 10),
        (1, 0),
    ], ids=["page=0", "page=-1", "size=0"])
    def test_order_pagination_boundary(self, admin_order_api, page, page_size):
        """订单分页参数边界"""
        resp = admin_order_api.get_orders(page=page, page_size=page_size)
        assert resp.status_code == 200