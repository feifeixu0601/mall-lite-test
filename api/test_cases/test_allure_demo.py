"""
Allure 报告演示

这个文件演示 Allure 的核心功能：
  1. severity - 严重级别分类
  2. feature/story - 功能/场景分类
  3. step - 步骤描述
  4. attach - 附加信息

知识点：Allure 报告中的层级关系
  feature（功能模块）
    └── story（用户场景）
          └── test_case（测试用例）
                └── step（步骤）

  在 MallLite 中：
    feature = "商品管理"
    story = "商品搜索"
    test_case = "按关键词搜索"
    step = "发送搜索请求"、"验证返回结果"
"""

import allure
import pytest
from common.assertions import ApiAssertions
from common.extractor import Extractor


@allure.feature("商品管理")
class TestProductAllure:
    """商品接口 - Allure 报告演示"""

    @allure.story("商品列表")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.product
    def test_product_list(self, product_api, assert_api):
        """
        获取商品列表

        severity = BLOCKER（阻塞级）
        这意味着如果这条用例失败，其他所有商品相关的用例都不用跑了

        知识点：Allure 严重级别
          BLOCKER   - 阻塞级：失败后其他用例无法执行
          CRITICAL  - 严重级：核心功能失败
          NORMAL    - 普通级：常规功能
          MINOR     - 次要级：非核心功能
          TRIVIAL   - 无关紧要：锦上添花的功能
        """
        with allure.step("发送获取商品列表请求"):
            resp = product_api.get_products()
            body = assert_api(resp).assert_success().body

        with allure.step("验证返回数据结构"):
            items = Extractor.get(body, "data.items")
            assert len(items) > 0, "商品列表不应为空"

        with allure.step("附加响应数据到报告"):
            allure.attach(
                name="商品列表响应",
                body=str(body)[:500],
                attachment_type=allure.attachment_type.TEXT,
            )

    @allure.story("商品搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.product
    @pytest.mark.parametrize("keyword", ["iPhone", "华为", "AirPods"],
                             ids=["iPhone", "华为", "AirPods"])
    def test_product_search(self, product_api, keyword):
        """
        数据驱动搜索

        severity = CRITICAL（严重级）
        搜索是核心功能，但不影响其他模块
        """
        with allure.step(f"搜索关键词：{keyword}"):
            resp = product_api.get_products(keyword=keyword)
            body = resp.json()

        with allure.step("验证搜索成功"):
            assert body["code"] == 200

        with allure.step("验证有搜索结果"):
            items = body["data"]["items"]
            assert len(items) > 0, f"搜索 '{keyword}' 无结果"

    @allure.story("商品详情")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.product
    def test_product_detail(self, product_api, assert_api):
        """
        查看商品详情

        severity = NORMAL（普通级）
        """
        with allure.step("获取商品列表"):
            resp = product_api.get_products(page_size=1)
            product_id = assert_api(resp).get_field("data.items")[0]["id"]

        with allure.step(f"查看商品 {product_id} 的详情"):
            resp = product_api.get_product(product_id)
            a = assert_api(resp)
            a.assert_success()

        with allure.step("验证详情数据完整"):
            a.assert_has_field("data.name")
            a.assert_has_field("data.price")
            a.assert_has_field("data.stock")


@allure.feature("购物车")
class TestCartAllure:
    """购物车接口 - Allure 报告演示"""

    @allure.story("添加商品")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.cart
    def test_add_to_cart(self, admin_cart_api, assert_api):
        """
        添加商品到购物车

        用 step 装饰器把操作分成清晰的步骤
        """
        with allure.step("添加商品 ID=1 到购物车"):
            resp = admin_cart_api.add_to_cart(product_id=1, quantity=2)
            assert_api(resp).assert_success()

        with allure.step("验证购物车中有该商品"):
            resp = admin_cart_api.get_cart()
            items = assert_api(resp).get_field("data.items")
            product_ids = [i["product_id"] for i in items]
            assert 1 in product_ids

        with allure.step("验证数量正确"):
            item = next(i for i in items if i["product_id"] == 1)
            assert item["quantity"] == 2


@allure.feature("订单")
class TestOrderAllure:
    """订单接口 - Allure 报告演示"""

    @allure.story("创建订单")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.order
    def test_create_order(self, admin_cart_api, admin_order_api, assert_api):
        """
        创建订单

        severity = BLOCKER：下单是购物流程的最后一步，失败意味着用户无法完成购买
        """
        with allure.step("清空购物车并添加商品"):
            admin_cart_api.clear_cart()
            admin_cart_api.add_to_cart(product_id=1, quantity=1)

        with allure.step("创建订单"):
            resp = admin_order_api.create_order()
            a = assert_api(resp)
            a.assert_success()

        with allure.step("验证订单号格式"):
            order_no = a.get_field("data.order_no")
            assert "ORD" in order_no
            allure.attach(name="订单号", body=order_no,
                          attachment_type=allure.attachment_type.TEXT)