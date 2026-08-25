"""
公共 Step Definitions
多个 Feature 共用的步骤
"""

from behave import given, when, then


@given('我打开地址 "{url}"')
def step_open_url(context, url):
    """打开指定地址"""
    context.page.goto(url)


@when('我等待 {seconds:d} 秒')
def step_wait(context, seconds):
    """等待指定秒数"""
    context.page.wait_for_timeout(seconds * 1000)


@then('页面标题应该包含 "{text}"')
def step_title_contains(context, text):
    """验证页面标题"""
    title = context.page.title()
    assert text in title, f"标题 '{title}' 不包含 '{text}'"


@then('当前 URL 应该包含 "{text}"')
def step_url_contains(context, text):
    """验证 URL"""
    url = context.page.url
    assert text in url, f"URL '{url}' 不包含 '{text}'"