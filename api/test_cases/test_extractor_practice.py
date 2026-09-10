"""
Extractor 实战

核心场景：
  1. 搜索 → 提取第一个商品 → 查详情（列表→详情的数据传递）
  2. 分类 → 提取分类 ID → 按分类筛选（动态获取 ID，不硬编码）
  3. 批量提取所有价格 → 验证合理性
  4. 购物车添加 → 提取验证（从响应中提取数据做验证）
"""

import pytest
from common.assertions import ApiAssertions
from common.extractor import Extractor


class TestSearchThenDetail:
    """场景 1：搜索 → 提取 → 查详情"""

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.p1
    def test_search_extract_then_detail(self, product_api, assert_api):
        """
        搜索商品 → 提取第一个 → 查详情

        这是最常见的接口关联场景：
        前端先调列表接口，用户点击某个商品后调详情接口。

        为什么用 Extractor 而不是直接取值？
          1. Extractor.get 在路径不存在时返回 None，不会崩溃
          2. 路径字符串可以复用和传递
          3. 代码意图更清晰
        """
        # 第一步：搜索
        resp = product_api.get_products(keyword="iPhone")
        body = assert_api(resp).assert_success().body

        # 第二步：用 Extractor 提取（不会因为搜索结果为空而崩溃）
        first = Extractor.first(body, "data.items")
        assert first is not None, "搜索结果为空"
        product_id = first["id"]
        product_name = first["name"]

        # 第三步：用提取到的数据查详情
        resp = product_api.get_product(product_id)
        a = assert_api(resp)
        a.assert_success()
        a.assert_field_value("data.name", product_name)
        a.assert_field_gt("data.price", 0)

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.p1
    def test_search_extract_all_prices(self, product_api):
        """
        批量提取所有商品价格，验证都大于 0

        对比手动写法：
          names = []
          for item in resp.json()["data"]["items"]:
              names.append(item["name"])

        Extractor 一行搞定，而且路径错了会返回空列表，不会崩溃
        """
        resp = product_api.get_products(page_size=20)
        body = resp.json()

        names = Extractor.get_all(body, "data.items.*.name")
        prices = Extractor.get_all(body, "data.items.*.price")

        assert len(names) > 0, "商品列表为空"
        assert len(names) == len(prices), "name 和 price 数量不一致"

        for name, price in zip(names, prices):
            assert price > 0, f"商品 '{name}' 价格应 > 0，实际 {price}"


class TestCategoryThenFilter:
    """场景 2：分类 → 提取 → 筛选"""

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.p1
    def test_category_extract_then_filter(self, product_api, assert_api):
        """
        获取分类列表 → 提取分类 ID → 按分类筛选商品

        设计思路：
          分类 ID 不是固定的，不能硬编码。
          如果写死 category_id=1，哪天分类数据变了用例就挂。
          从分类列表中动态提取，用例就不会因为 ID 变化而失败。
        """
        # 获取分类列表
        resp = product_api.get_categories()
        body = assert_api(resp).assert_success().body

        # 动态提取第一个分类的 ID
        categories = body["data"]
        assert len(categories) > 0, "分类列表为空"
        category_id = categories[0]["id"]
        category_name = categories[0]["name"]

        # 用提取到的 ID 筛选商品
        resp = product_api.get_products(category_id=category_id)
        a = assert_api(resp)
        a.assert_success()
        a.assert_list_not_empty("data.items")


class TestCartExtractor:
    """场景 3：购物车场景的 Extractor 用法"""

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.p1
    def test_add_then_extract_and_verify(self, admin_cart_api, assert_api):
        """
        添加商品 → 从购物车响应中提取该商品 → 验证数量

        演示：从列表中按条件提取特定元素的用法
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=3)

        resp = admin_cart_api.get_cart()
        body = assert_api(resp).assert_success().body

        # 提取所有 product_id
        all_ids = Extractor.get_all(body, "data.items.*.product_id")
        assert 1 in all_ids, "购物车中应包含商品 1"

        # 提取所有数量，找到商品 1 对应的数量
        all_quantities = Extractor.get_all(body, "data.items.*.quantity")
        idx = all_ids.index(1)
        assert all_quantities[idx] == 3, f"数量应为 3，实际 {all_quantities[idx]}"