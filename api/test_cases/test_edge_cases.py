"""
边界值和异常场景

设计思路：
  对每个业务接口，按五个维度逐个思考：
  1. 空值    2. 范围    3. 不存在    4. 恶意输入    5. 状态冲突

  不需要每个维度都覆盖每个接口，选择该接口最容易出问题的维度。
  比如登录重点测空值和恶意输入，购物车重点测范围和不存在。
"""

import pytest


class TestCartEdgeCases:
    """
    购物车边界值

    购物车的"数量"参数是最容易出问题的——前端可能传 0、负数、极大数。
    服务端必须能正确处理这些异常值。
    """

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.negative
    @pytest.mark.parametrize("quantity,label", [
        (0, "数量=0"),
        (-1, "数量=-1"),
        (-100, "数量=-100"),
        (99999, "数量=99999"),
    ], ids=["数量=0", "数量=-1", "数量=-100", "数量=99999"])
    def test_add_quantity_boundary(self, admin_cart_api, quantity, label):
        """
        维度 2：数量的范围边界

        不管成功还是失败，接口不应该崩溃（HTTP 500）。
        如果服务端做了校验（拒绝 0 和负数），code 应该 != 200。
        如果服务端没做校验，至少不该返回 500。
        """
        resp = admin_cart_api.add_to_cart(product_id=1, quantity=quantity)
        assert resp.status_code == 200, f"{label} 导致 HTTP {resp.status_code}"

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.negative
    def test_add_nonexistent_product(self, admin_cart_api, assert_api):
        """
        维度 3：不存在的商品 ID

        应该返回业务失败（商品不存在），而不是服务端报错
        """
        resp = admin_cart_api.add_to_cart(product_id=999999, quantity=1)
        assert_api(resp).assert_biz_fail()

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.negative
    def test_update_nonexistent_product(self, admin_cart_api):
        """
        维度 5：修改一个不在购物车中的商品

        不管返回什么，不应该崩溃
        """
        resp = admin_cart_api.update_quantity(product_id=999999, quantity=5)
        assert resp.status_code == 200

    @pytest.mark.regression
    @pytest.mark.cart
    @pytest.mark.negative
    def test_delete_nonexistent_product(self, admin_cart_api):
        """维度 5：删除一个不在购物车中的商品"""
        resp = admin_cart_api.delete_from_cart(product_id=999999)
        assert resp.status_code == 200


class TestOrderEdgeCases:
    """
    订单边界值

    订单最特殊的边界是"状态冲突"——购物车为空时下单、连续下单两次。
    """

    @pytest.mark.regression
    @pytest.mark.order
    @pytest.mark.negative
    def test_order_empty_cart(self, admin_order_api, assert_api):
        """
        维度 1：空购物车下单

        探针确认：code=400, message=购物车为空
        这是一个"前置条件不满足"的场景
        """
        resp = admin_order_api.create_order()
        a = assert_api(resp)
        a.assert_biz_fail()
        a.assert_code(400)
        a.assert_message("购物车为空")

    @pytest.mark.regression
    @pytest.mark.order
    @pytest.mark.negative
    def test_order_twice(self, admin_cart_api, admin_order_api, assert_api):
        """
        维度 5：连续下单两次

        设计思路：
          第一次下单成功后，购物车应该被清空。
          第二次下单时购物车为空，应该失败。
          这验证的是"下单后购物车自动清空"这个隐含逻辑。
          如果服务端没有清空购物车，第二次也会成功，但这是个 bug（扣两次库存）。
        """
        admin_cart_api.add_to_cart(product_id=1, quantity=1)

        # 第一次下单
        resp = admin_order_api.create_order()
        assert_api(resp).assert_success()

        # 第二次下单（购物车应已清空）
        resp = admin_order_api.create_order()
        assert_api(resp).assert_biz_fail()

    @pytest.mark.regression
    @pytest.mark.order
    @pytest.mark.negative
    def test_query_nonexistent_order(self, admin_order_api):
        """
        维度 3：查询不存在的订单号

        不应该崩溃，应该返回合理的响应
        """
        resp = admin_order_api.get_order("ORD_NOT_EXIST_999")
        assert resp.status_code == 200


class TestLoginEdgeCases:
    """
    登录边界值

    登录的边界主要在输入格式和重复操作上。
    """

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.negative
    def test_login_twice(self, user_api, assert_api, admin_account):
        """
        维度 5：已登录状态再次登录

        不应出错，应正常返回。
        有的系统会返回"已登录"提示，有的会静默刷新 session。
        不管哪种，不应该报错。
        """
        resp = user_api.login(admin_account["username"], admin_account["password"])
        assert_api(resp).assert_success()

        # 第二次登录（同一个 session）
        resp = user_api.login(admin_account["username"], admin_account["password"])
        assert_api(resp).assert_success()

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.negative
    @pytest.mark.parametrize("username,password", [
        (" admin ", "admin123"),
        ("ADMIN", "admin123"),
        ("Admin", "admin123"),
    ], ids=["前后空格", "全大写", "首字母大写"])
    def test_login_input_variation(self, user_api, username, password):
        """
        维度 2：输入格式变体

        验证服务端是否做输入标准化（trim、大小写转换）。
        不管成功还是失败，接口不应该崩溃。
        """
        resp = user_api.login(username, password)
        assert resp.status_code == 200

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.negative
    @pytest.mark.parametrize("username,password", [
        ("admin' OR '1'='1", "123"),
        ("<script>alert(1)</script>", "123"),
        ("a" * 256, "123"),
    ], ids=["SQL注入", "XSS", "超长用户名"])
    def test_login_malicious(self, user_api, username, password):
        """
        维度 4：恶意输入不导致服务端崩溃

        SQL 注入：如果服务端没有做参数化查询，可能被注入成功
        XSS：如果返回值原样返回给前端，可能被执行
        超长字符串：可能导致内存溢出或数据库字段截断

        这里只验证不会返回 HTTP 500。
        安全测试还需要更专业的工具（如 sqlmap、OWASP ZAP）。
        """
        resp = user_api.login(username, password)
        assert resp.status_code == 200