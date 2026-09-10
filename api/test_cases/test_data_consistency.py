"""
跨接口数据一致性验证

核心思路：同一条数据从不同接口拿到的应该一致
  - 商品：列表 vs 详情
  - 订单：列表 vs 详情
  - 购物车/订单：总数 vs 各项之和

为什么单独一个文件？
  一致性验证是一个独立的关注点。
  如果放在 test_product.py 或 test_order.py 里，容易被淹没在其他用例中。
  单独一个文件能一目了然地看到所有一致性验证。
"""

import pytest


class TestProductConsistency:
    """商品数据一致性"""

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.p1
    def test_product_list_vs_detail(self, product_api, assert_api):
        """
        商品列表中的 name/price 跟详情接口的 name/price 应该一致

        设计思路：
          从列表中取第一个商品，记录它的 name 和 price。
          再用它的 id 调详情接口，对比 name 和 price。
          两者必须完全相同。
        """
        # 从列表获取
        resp = product_api.get_products(page_size=1)
        list_item = assert_api(resp).get_field("data.items")[0]
        list_id = list_item["id"]
        list_name = list_item["name"]
        list_price = list_item["price"]

        # 从详情获取
        resp = product_api.get_product(list_id)
        detail = assert_api(resp).get_field("data")

        # 对比（逐字段比较，失败时报错信息能告诉你哪个字段不一致）
        assert detail["name"] == list_name, \
            f"名称不一致：列表='{list_name}', 详情='{detail['name']}'"
        assert detail["price"] == list_price, \
            f"价格不一致：列表={list_price}, 详情={detail['price']}"

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.p1
    def test_search_result_vs_detail(self, product_api, assert_api):
        """
        搜索结果和详情的数据一致性

        搜索用 keyword="iPhone"，取第一个结果，跟详情对比
        这跟列表 vs 详情是不同路径（搜索走的是 /products?keyword=，
        列表走的是 /products?page=1），所以需要分别验证
        """
        resp = product_api.get_products(keyword="iPhone")
        items = assert_api(resp).get_field("data.items")
        assert len(items) > 0, "搜索无结果"
        first = items[0]

        resp = product_api.get_product(first["id"])
        detail = assert_api(resp).get_field("data")

        assert detail["name"] == first["name"]
        assert detail["price"] == first["price"]

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.p1
    @pytest.mark.parametrize("category_id", [1, 2, 3], ids=["手机", "笔记本", "平板"])
    def test_category_filter_consistency(self, product_api, assert_api, category_id):
        """
        数据驱动：分类筛选结果中每个商品的详情也应该一致

        知识点：pytest.mark.parametrize
          @pytest.mark.parametrize("category_id", [1, 2, 3], ids=["手机", "笔记本", "平板"])
          这会生成 3 条用例，分别用 category_id=1、2、3 执行。
          ids 参数让用例名更可读（不然会显示 test_xxx[1]、test_xxx[2]）。
        """
        resp = product_api.get_products(category_id=category_id, page_size=1)
        items = assert_api(resp).get_field("data.items")

        if len(items) == 0:
            pytest.skip(f"分类 {category_id} 下没有商品")
            # pytest.skip() 跳过用例但不算失败
            # 适用于依赖数据存在但数据可能不存在的场景

        first = items[0]
        resp = product_api.get_product(first["id"])
        detail = assert_api(resp).get_field("data")

        assert detail["name"] == first["name"]
        assert detail["price"] == first["price"]


class TestOrderConsistency:
    """订单数据一致性"""

    @pytest.mark.regression
    @pytest.mark.order
    @pytest.mark.p1
    def test_order_list_vs_detail(self, admin_order_api, assert_api, created_order):
        """
        订单列表中的 status 跟详情接口应该一致

        用 created_order fixture 保证有订单数据
        """
        order_no = created_order

        # 从列表找到
        resp = admin_order_api.get_orders()
        list_items = assert_api(resp).get_field("data.items")
        list_order = next((o for o in list_items if o["order_no"] == order_no), None)
        assert list_order is not None, f"列表中找不到订单 {order_no}"

        # 从详情获取
        resp = admin_order_api.get_order(order_no)
        detail = assert_api(resp).get_field("data")

        # 对比
        assert list_order["status"] == detail["status"], \
            f"状态不一致：列表='{list_order['status']}', 详情='{detail['status']}'"
        assert list_order["order_no"] == detail["order_no"]

    @pytest.mark.regression
    @pytest.mark.order
    @pytest.mark.p1
    def test_order_total_equals_subtotals(self, admin_cart_api, admin_order_api, assert_api):
        """
        订单总金额 = 各商品小计之和

        这是金额计算正确性验证。
        如果服务端算错了总价（比如少算了运费、多算了折扣），这条用例会失败。

        知识点：为什么用 .get("subtotal", ...) ？
          因为不一定所有服务端都返回 subtotal 字段。
          如果没有 subtotal，就用 price * quantity 自己算。
          这种防御性写法让用例更健壮。
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=2)

        resp = admin_order_api.create_order()
        order_no = assert_api(resp).get_field("data.order_no")

        resp = admin_order_api.get_order(order_no)
        a = assert_api(resp)
        items = a.get_field("data.items")
        total = a.get_field("data.total_price")

        # 计算各项小计之和
        items_sum = sum(
            item.get("subtotal", item["price"] * item["quantity"])
            for item in items
        )
        assert items_sum == total, \
            f"小计之和 ({items_sum}) != 总金额 ({total})"


class TestCartConsistency:
    """购物车数据一致性"""

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.p1
    def test_cart_total_quantity(self, admin_cart_api, assert_api):
        """
        total_quantity = 各商品 quantity 之和

        添加两个不同数量的商品，验证服务端算对了
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=2)
        admin_cart_api.add_to_cart(product_id=2, quantity=3)

        resp = admin_cart_api.get_cart()
        a = assert_api(resp)

        items = a.get_field("data.items")
        total = a.get_field("data.total_quantity")

        expected = sum(item["quantity"] for item in items)
        assert total == expected, f"total_quantity 期望 {expected}，实际 {total}"

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.p1
    def test_cart_item_count(self, admin_cart_api, assert_api):
        """
        item_count = 商品种类数（不是总数量）

        添加了 2 种商品（不同 product_id），item_count 应该是 2。
        如果 item_count 返回的是 8（2+3+3？），说明服务端把 item_count 和 total_quantity 搞混了。
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=5)
        admin_cart_api.add_to_cart(product_id=2, quantity=3)

        resp = admin_cart_api.get_cart()
        a = assert_api(resp)

        items = a.get_field("data.items")
        item_count = a.get_field("data.item_count")
        assert item_count == len(items), \
            f"item_count 期望 {len(items)}（种类数），实际 {item_count}"