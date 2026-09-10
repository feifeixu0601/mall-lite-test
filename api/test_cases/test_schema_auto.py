"""
Schema 自动校验实战

两种方式：
  1. assert_schema() 手动校验（第 10 篇已用）
  2. generate_schema() 自动生成 Schema 骨架
"""

import pytest
import json
from common.schemas import validate_schema, generate_schema
from common.assertions import ApiAssertions


class TestSchemaManual:
    """手动 Schema 校验（回顾）"""

    @pytest.mark.regression
    @pytest.mark.schema
    def test_login_schema(self, user_api, assert_api, admin_account):
        """
        手动校验：登录响应符合 Schema

        知识点：为什么每个接口都要校验 Schema？
          Schema 校验不是检查"数据对不对"，而是检查"格式对不对"。
          如果接口返回了 {"code": 200} 但没有 "data" 字段，
          后面的 get_field("data.username") 会直接报错。
          Schema 校验能提前发现这种结构变更。
        """
        resp = user_api.login(admin_account["username"], admin_account["password"])
        assert_api(resp).assert_success().assert_schema("login")

    @pytest.mark.regression
    @pytest.mark.schema
    def test_product_list_schema(self, product_api, assert_api):
        """手动校验：商品列表"""
        resp = product_api.get_products()
        assert_api(resp).assert_success().assert_schema("product_list")

    @pytest.mark.regression
    @pytest.mark.schema
    def test_cart_schema(self, admin_cart_api, assert_api):
        """手动校验：购物车"""
        admin_cart_api.add_to_cart(product_id=1, quantity=1)
        resp = admin_cart_api.get_cart()
        assert_api(resp).assert_success().assert_schema("cart")

    @pytest.mark.regression
    @pytest.mark.schema
    def test_category_schema(self, product_api, assert_api):
        """手动校验：分类列表"""
        resp = product_api.get_categories()
        assert_api(resp).assert_success().assert_schema("category_list")


class TestSchemaGenerate:
    """
    自动生成 Schema 骨架

    知识点：自动生成的工作流程
      1. 用 generate_schema(resp.json()) 生成骨架
      2. 检查生成的 Schema 是否合理
      3. 微调后复制到 schemas.py 中
      4. 后续用 assert_schema() 做回归校验
    """

    @pytest.mark.regression
    @pytest.mark.schema
    def test_generate_login_schema(self, user_api, admin_account):
        """生成登录响应的 Schema 骨架"""
        resp = user_api.login(admin_account["username"], admin_account["password"])
        body = resp.json()

        schema = generate_schema(body)

        # 验证骨架的基本结构
        assert schema["type"] == "object"
        assert "code" in schema["properties"]
        assert "message" in schema["properties"]
        assert "data" in schema["properties"]

        # 打印生成的 Schema（运行时可以看到）
        print(f"\n生成的登录 Schema：\n{json.dumps(schema, indent=2, ensure_ascii=False)}")

    @pytest.mark.regression
    @pytest.mark.schema
    def test_generate_product_list_schema(self, product_api):
        """生成商品列表的 Schema 骨架"""
        resp = product_api.get_products(page_size=1)
        body = resp.json()

        schema = generate_schema(body)

        assert schema["type"] == "object"
        assert "code" in schema["properties"]
        assert "data" in schema["properties"]

        print(f"\n生成的商品列表 Schema：\n{json.dumps(schema, indent=2, ensure_ascii=False)}")