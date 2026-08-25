"""
BDD 环境管理
管理浏览器生命周期、截图、日志等
相当于 Pytest 的 conftest.py
"""

import allure
from playwright.sync_api import sync_playwright

from common.logger import get_logger
from common.screenshot import Screenshot

logger = get_logger("bdd_env")

BASE_URL = "http://localhost:8000"          # ← 新增


def before_all(context):
    """
    所有场景执行前调用（整个测试会话一次）
    启动浏览器
    """
    logger.info("=" * 60)
    logger.info("BDD 测试会话开始")
    logger.info("=" * 60)

    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(
        headless=True,                      # ← 原文是 False
        slow_mo=0,
    )


def after_all(context):
    """所有场景执行后调用，关闭浏览器"""
    context.browser.close()
    context.playwright.stop()

    logger.info("=" * 60)
    logger.info("BDD 测试会话结束")
    logger.info("=" * 60)


def before_scenario(context, scenario):
    """
    每个场景执行前调用
    创建独立的浏览器上下文和页面
    """
    logger.info(f"--- 场景开始：{scenario.name} ---")

    context.context = context.browser.new_context(
        viewport={"width": 1280, "height": 720},
        base_url=BASE_URL,                  # ← 原文没有这行
    )
    context.page = context.context.new_page()
    context.page.set_default_timeout(10000)

    # 初始化页面对象（供 step 使用）
    from pages import LoginPage, HomePage, ProductPage, CartPage, OrderPage, ProfilePage
    context.login_page = LoginPage(context.page)
    context.home_page = HomePage(context.page)
    context.product_page = ProductPage(context.page)
    context.cart_page = CartPage(context.page)
    context.order_page = OrderPage(context.page)
    context.profile_page = ProfilePage(context.page)

    # 临时数据存储（场景间传递数据）
    context.data = {}


def after_scenario(context, scenario):
    """
    每个场景执行后调用
    失败时截图，关闭上下文
    """
    if scenario.status == "failed":
        logger.error(f"场景失败：{scenario.name}")
        try:
            screenshot_path = Screenshot.take(
                context.page,
                f"BDD失败_{scenario.name}",
                attach_to_allure=False,
            )
            if screenshot_path:
                # 附加到 Allure
                allure.attach.file(
                    str(screenshot_path),
                    name=f"失败截图_{scenario.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
        except Exception as e:
            logger.error(f"截图失败：{e}")
    else:
        logger.info(f"场景通过：{scenario.name}")

    # 关闭上下文
    context.context.close()
    logger.info(f"--- 场景结束：{scenario.name} ---")