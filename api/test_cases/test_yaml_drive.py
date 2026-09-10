"""
YAML 数据驱动用例

对比 JSON 数据驱动（第 10 篇的 test_user.py、test_product.py）：
  JSON：机器友好，不能写注释，适合 API 返回值
  YAML：人友好，能写注释，适合测试数据

知识点：什么时候用 YAML，什么时候用 JSON？
  测试数据 → YAML（需要注释说明每组数据的目的）
  API 返回值 → JSON（机器生成，不需要注释）
  配置文件 → YAML（需要注释，如 pytest.ini 的 YAML 版本）
"""

import pytest
from common.data_reader import read_yaml
from common.assertions import ApiAssertions

cart_data = read_yaml("cart_cases.yaml")
order_data = read_yaml("order_cases.yaml")


class TestCartYAML:
    """购物车 YAML 数据驱动"""

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.parametrize("case", cart_data["add_cases"],
                             ids=[c["case_name"] for c in cart_data["add_cases"]])
    def test_add_to_cart(self, admin_cart_api, assert_api, case):
        """
        YAML 驱动：添加购物车

        数据来自 test_data/cart_cases.yaml 的 add_cases
        新增数据只需改 YAML 文件，不改 Python 代码
        """
        resp = admin_cart_api.add_to_cart(
            product_id=case["product_id"],
            quantity=case["quantity"],
        )

        if case["expected_success"]:
            assert_api(resp).assert_success()
        else:
            assert_api(resp).assert_biz_fail()


class TestOrderYAML:
    """订单 YAML 数据驱动"""

    @pytest.mark.regression
    @pytest.mark.order
    @pytest.mark.parametrize("case", order_data["create_cases"],
                             ids=[c["case_name"] for c in order_data["create_cases"]])
    def test_create_order(self, admin_cart_api, admin_order_api, assert_api, case):
        """
        YAML 驱动：创建订单

        数据中的 add_product_id 为 null 表示不加购物车（测试空购物车下单）
        """
        # 如果指定了商品，先加购物车
        if case["add_product_id"]:
            admin_cart_api.add_to_cart(
                product_id=case["add_product_id"],
                quantity=case["add_quantity"],
            )

        resp = admin_order_api.create_order()

        if case["expected_success"]:
            assert_api(resp).assert_success()
        else:
            assert_api(resp).assert_biz_fail()
            if case.get("expected_msg"):
                assert_api(resp).assert_message(case["expected_msg"])