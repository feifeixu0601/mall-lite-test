"""
Excel 数据驱动用例

核心价值：非技术人员（产品、业务测试）可以直接编辑 Excel 来修改测试数据，
不需要懂 Python、不需要懂 YAML 格式。

使用方式：
  1. 产品同学打开 test_data/login_cases.xlsx
  2. 在 Sheet "登录失败" 中新增一行数据
  3. 保存 Excel
  4. 运行 pytest，自动多一条用例

知识点：Excel vs YAML vs JSON 对比
  JSON：机器友好，不能写注释，Git 友好
  YAML：人友好，能写注释，Git 友好
  Excel：非技术人员友好，不能版本控制（二进制文件），不适合 CI/CD

  建议：CI/CD 用 YAML，线下跟业务同学协作用 Excel
"""

import pytest
from common.data_reader import read_excel
from common.assertions import ApiAssertions

# 读取 Excel 中两个 Sheet 的数据
login_success = read_excel("login_cases.xlsx", "登录成功")
login_fail = read_excel("login_cases.xlsx", "登录失败")


class TestLoginExcel:
    """Excel 数据驱动：登录接口"""

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.parametrize("case", login_success,
                             ids=[c["case_name"] for c in login_success])
    def test_login_success(self, user_api, assert_api, case):
        """
        Excel 驱动：多种用户类型登录成功

        数据来自 test_data/login_cases.xlsx 的 "登录成功" Sheet
        """
        resp = user_api.login(case["username"], case["password"])

        a = assert_api(resp)
        a.assert_success()
        a.assert_field_value("data.username", case["username"])
        a.assert_field_value("data.role", case["expected_role"])

    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.negative
    @pytest.mark.parametrize("case", login_fail,
                             ids=[c["case_name"] for c in login_fail])
    def test_login_fail(self, user_api, assert_api, case):
        """
        Excel 驱动：各种登录失败场景

        数据来自 test_data/login_cases.xlsx 的 "登录失败" Sheet
        """
        resp = user_api.login(case["username"], case["password"])

        a = assert_api(resp)
        a.assert_biz_fail()
        a.assert_code(401)
        a.assert_message(case["expected_msg"])