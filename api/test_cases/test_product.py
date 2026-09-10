"""
商品接口测试（数据驱动版 + Schema 校验）
"""

import pytest
from common.data_reader import read_json
from common.schemas import validate_schema

product_data = read_json("product_cases.json")


class TestProductList:

    @pytest.mark.smoke
    @pytest.mark.product
    @pytest.mark.p0
    def test_get_product_list(self, product_api, assert_api):
        resp = product_api.get_products()
        a = assert_api(resp)
        a.assert_success()
        a.assert_list_not_empty("data.items")
        a.assert_schema("product_list")

    @pytest.mark.smoke
    @pytest.mark.product
    def test_get_product_detail(self, product_api, assert_api):
        resp = product_api.get_products(page_size=1)
        first_id = assert_api(resp).get_field("data.items")[0]["id"]

        resp = product_api.get_product(first_id)
        a = assert_api(resp)
        a.assert_success()
        a.assert_field_gt("data.price", 0)
        a.assert_schema("product_detail")

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.parametrize("case", product_data["search_cases"],
                             ids=[c["keyword"] for c in product_data["search_cases"]])
    def test_search_by_keyword(self, product_api, assert_api, case):
        resp = product_api.get_products(keyword=case["keyword"])
        a = assert_api(resp)
        a.assert_success()
        a.assert_list_min_length("data.items", case["min_count"])

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.negative
    def test_search_no_result(self, product_api, assert_api):
        resp = product_api.get_products(keyword="xyz_not_exist_999")
        a = assert_api(resp)
        a.assert_success()
        assert len(a.get_field("data.items")) == 0

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.parametrize("case", product_data["category_cases"],
                             ids=[c["name"] for c in product_data["category_cases"]])
    def test_filter_by_category(self, product_api, assert_api, case):
        resp = product_api.get_products(category_id=case["category_id"])
        a = assert_api(resp)
        a.assert_success()
        a.assert_list_min_length("data.items", case["min_count"])

    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.p2
    def test_pagination(self, product_api, assert_api):
        r1 = product_api.get_products(page=1, page_size=3)
        r2 = product_api.get_products(page=2, page_size=3)
        ids1 = {i["id"] for i in assert_api(r1).get_field("data.items")}
        ids2 = {i["id"] for i in assert_api(r2).get_field("data.items")}
        if ids1 and ids2:
            assert ids1 != ids2

    @pytest.mark.smoke
    @pytest.mark.category
    def test_get_categories(self, product_api, assert_api):
        resp = product_api.get_categories()
        a = assert_api(resp)
        a.assert_success()
        a.assert_schema("category_list")
        assert len(a.get_data()) >= 4