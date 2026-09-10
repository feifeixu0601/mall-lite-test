"""
用户接口测试（数据驱动版 + Schema 校验）
"""

import pytest
import time
from common.data_reader import read_json
from common.schemas import validate_schema

login_data = read_json("login_cases.json")
success_cases = login_data["success_cases"]
fail_cases = login_data["fail_cases"]


class TestLogin:

    @pytest.mark.smoke
    @pytest.mark.login
    @pytest.mark.p0
    @pytest.mark.parametrize("case", success_cases,
                             ids=[c["case_name"] for c in success_cases])
    def test_login_success(self, user_api, assert_api, case):
        """数据驱动：多种用户类型登录"""
        resp = user_api.login(case["username"], case["password"])

        a = assert_api(resp)
        a.assert_success()
        a.assert_field_value("data.username", case["username"])
        a.assert_field_value("data.role", case["expected_role"])
        a.assert_schema("login")

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.negative
    @pytest.mark.parametrize("case", fail_cases,
                             ids=[c["case_name"] for c in fail_cases])
    def test_login_fail(self, user_api, assert_api, case):
        """数据驱动：各种登录失败场景"""
        resp = user_api.login(case["username"], case["password"])

        a = assert_api(resp)
        a.assert_biz_fail()
        a.assert_code(case["expected_code"])
        a.assert_message(case["expected_msg"])

    @pytest.mark.smoke
    @pytest.mark.login
    def test_login_session_persists(self, user_api, assert_api, admin_account):
        """登录后 Cookie 能保持"""
        user_api.login(admin_account["username"], admin_account["password"])
        resp = user_api.get("/api/cart")
        assert resp.json()["code"] == 200

    @pytest.mark.regression
    @pytest.mark.login
    def test_login_roles(self, user_api, assert_api):
        """所有角色都能登录"""
        for case in success_cases:
            resp = user_api.login(case["username"], case["password"])
            assert_api(resp).assert_success().assert_field_value("data.role", case["expected_role"])

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.negative
    @pytest.mark.parametrize("username,password", [
        ("admin' OR '1'='1", "123"),
        ("<script>alert(1)</script>", "123"),
        ("a" * 256, "123"),
    ], ids=["SQL注入", "XSS", "超长用户名"])
    def test_login_malicious(self, user_api, username, password):
        """恶意输入不导致服务端崩溃"""
        resp = user_api.login(username, password)
        assert resp.status_code == 200

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.schema
    def test_login_response_schema(self, user_api, admin_account):
        """Schema 校验：登录响应结构"""
        resp = user_api.login(admin_account["username"], admin_account["password"])
        validate_schema(resp.json(), "login")


class TestRegister:

    @pytest.mark.regression
    @pytest.mark.register
    def test_register_success(self, user_api, assert_api):
        resp = user_api.register(f"auto_{int(time.time())}", "Test123456")
        assert_api(resp).assert_success()

    @pytest.mark.regression
    @pytest.mark.register
    @pytest.mark.negative
    def test_register_duplicate(self, user_api, assert_api):
        resp = user_api.register("admin", "123456")
        assert_api(resp).assert_biz_fail()