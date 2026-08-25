"""
登录功能 Step Definitions
把 Feature 文件中的自然语言映射到页面对象操作
"""

from behave import given, when, then
from playwright.sync_api import expect


# ========================================
# Given 步骤
# ========================================

@given('我在登录页面')
def step_open_login_page(context):
    """打开登录页"""
    context.login_page.open()


# ========================================
# When 步骤
# ========================================

@when('我输入用户名 "{username}" 和密码 "{password}"')
def step_input_credentials(context, username, password):
    """输入用户名和密码"""
    actual_username = "" if username == "NONE" else username
    actual_password = "" if password == "NONE" else password
    context.login_page.input_username(actual_username)
    context.login_page.input_password(actual_password)


@when('我输入用户名空值和密码 "{password}"')
def step_input_empty_username(context, password):
    """输入空用户名"""
    context.login_page.input_username("")
    context.login_page.input_password(password)


@when('我输入用户名 "{username}" 和密码空值')
def step_input_empty_password(context, username):
    """输入空密码"""
    context.login_page.input_username(username)
    context.login_page.input_password("")


@when('我点击登录按钮')
def step_click_login(context):
    """点击登录"""
    # 禁用浏览器 HTML5 原生验证，确保空值也能提交到后端
    context.page.evaluate(
        "document.querySelector('form[action=\"/login\"]').setAttribute('novalidate', '')"
    )
    context.login_page.click_login()


# ========================================
# Then 步骤
# ========================================

@then('我应该成功登录并跳转到首页')
def step_verify_login_success(context):
    """验证登录成功"""
    assert context.login_page.is_login_success(), \
        f"登录失败，当前 URL：{context.page.url}"


@then('我应该看到错误提示 "{expected_msg}"')
def step_verify_error_message(context, expected_msg):
    """验证错误提示"""
    actual_msg = context.login_page.get_error_message()
    assert expected_msg in actual_msg, \
        f"期望错误提示包含 '{expected_msg}'，实际为 '{actual_msg}'"


@then('我应看到错误提示 "{expected_msg}"')
def step_verify_error_message2(context, expected_msg):
    """验证错误提示（别名）"""
    actual_msg = context.login_page.get_error_message()
    assert expected_msg in actual_msg, \
        f"期望错误提示包含 '{expected_msg}'，实际为 '{actual_msg}'"


@then('我应该看到结果 "{result}"')
def step_verify_login_result(context, result):
    """验证登录结果（参数化场景用）"""
    if result == "成功":
        assert context.login_page.is_login_success(), "应该登录成功"
    else:
        assert not context.login_page.is_login_success(), "不应该登录成功"
        actual_msg = context.login_page.get_error_message()
        assert result in actual_msg, \
            f"期望错误提示包含 '{result}'，实际为 '{actual_msg}'"