"""
登录功能测试（POM 模式）

使用 LoginPage 页面对象编写
所有用例不包含任何元素定位代码
"""

import pytest
from common.data_reader import DataReader
from common.allure_helper import AllureHelper


# 加载测试数据
login_data = DataReader.read_json("login_data.json")
success_cases = [c for c in login_data if c["expected"] == "success"]
fail_cases = [c for c in login_data if c["expected"] == "fail"]


@pytest.mark.login
class TestLogin:
    """登录功能测试集"""

    # ========================================
    # 正向用例
    # ========================================

    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.parametrize("case", success_cases,
                             ids=[c["case_name"] for c in success_cases])
    def test_login_success(self, login_page, home_page, case):
        """
        验证各种用户能正常登录

        数据驱动：遍历 login_data.json 中 expected=success 的用例

        步骤：
            1. 打开登录页
            2. 输入正确的用户名和密码
            3. 点击登录
            4. 验证跳转到首页
        """
        AllureHelper.title(case["case_name"], case.get("description", ""))
        AllureHelper.severity("critical")
        AllureHelper.feature("登录")
        AllureHelper.story("正常登录")

        # 执行登录
        login_page.login(case["username"], case["password"])

        # 验证登录成功
        assert login_page.is_login_success(), \
            f"用户 {case['username']} 登录失败，当前 URL：{login_page.get_current_url()}"

    # ========================================
    # 反向用例
    # ========================================

    @pytest.mark.p1
    @pytest.mark.parametrize("case", fail_cases,
                             ids=[c["case_name"] for c in fail_cases])
    def test_login_fail(self, login_page, case):
        """
        验证各种登录失败场景

        数据驱动：遍历 login_data.json 中 expected=fail 的用例

        步骤：
            1. 打开登录页
            2. 输入错误的用户名/密码
            3. 点击登录
            4. 验证显示错误提示
        """
        AllureHelper.title(case["case_name"], case.get("description", ""))
        AllureHelper.severity("normal")
        AllureHelper.feature("登录")
        AllureHelper.story("异常登录")

        # 执行登录
        login_page.login(case["username"], case["password"])

        # 验证登录失败
        assert not login_page.is_login_success(), \
            f"用户 {case['username']} 不应该登录成功"

        # 验证错误提示
        if "expected_msg" in case:
            error_msg = login_page.get_error_message()
            assert case["expected_msg"] in error_msg, \
                f"期望错误提示包含 '{case['expected_msg']}'，实际为 '{error_msg}'"

    # ========================================
    # 边界用例
    # ========================================

    @pytest.mark.regression
    @pytest.mark.p2
    def test_login_page_elements(self, login_page):
        """
        验证登录页面元素完整性

        步骤：
            1. 打开登录页
            2. 验证用户名输入框可见
            3. 验证密码输入框可见
            4. 验证登录按钮可见
        """
        AllureHelper.title("登录页面元素验证")
        AllureHelper.feature("登录")

        login_page.open()

        login_page.expect_visible(login_page.INPUT_USERNAME)
        login_page.expect_visible(login_page.INPUT_PASSWORD)
        login_page.expect_visible(login_page.BTN_LOGIN)

    @pytest.mark.regression
    @pytest.mark.p2
    def test_login_password_masked(self, login_page):
        """
        验证密码输入框是密文显示

        步骤：
            1. 打开登录页
            2. 验证密码输入框的 type 为 password
        """
        AllureHelper.title("密码输入框密文验证")
        AllureHelper.feature("登录")

        login_page.open()
        input_type = login_page.get_attribute(login_page.INPUT_PASSWORD, "type")
        assert input_type == "password", f"密码输入框类型应为 password，实际为 {input_type}"