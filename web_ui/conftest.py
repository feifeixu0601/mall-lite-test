"""
conftest.py - Pytest 核心配置（更新版）
集成配置管理、日志、截图、Allure 报告、POM 页面对象
"""

import pytest
import allure
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

from config.config import Config
from common.logger import get_logger
from common.screenshot import Screenshot
from common.allure_helper import AllureHelper
from pages import LoginPage, HomePage, ProductPage, CartPage, OrderPage, ProfilePage  # ← 新增

logger = get_logger("conftest")


# ========================================
# 命令行参数注册
# ========================================

def pytest_addoption(parser):
    """注册自定义命令行参数"""
    parser.addoption("--browser", action="store", default="chromium",
                     choices=["chromium", "firefox", "webkit"],
                     help="浏览器类型：chromium / firefox / webkit")
    parser.addoption("--headed", action="store", default="false",
                     choices=["true", "false"],
                     help="是否显示浏览器窗口：true / false")
    parser.addoption("--base-url", action="store", default="http://localhost:8000",
                     help="被测系统地址")
    parser.addoption("--slow-mo", action="store", default="0",
                     help="操作间隔（毫秒），调试时设为 500")
    parser.addoption("--env", action="store", default="dev",
                     choices=["dev", "staging", "prod"],
                     help="测试环境：dev / staging / prod")


# ========================================
# 配置 Fixture
# ========================================

@pytest.fixture(scope="session")
def config(request):
    """
    配置对象（整个测试会话共享）
    集成命令行参数和配置文件
    """
    # 收集命令行参数
    cli_options = {
        "--base-url": request.config.getoption("--base-url"),
        "--browser": request.config.getoption("--browser"),
        "--headed": request.config.getoption("--headed"),
        "--slow-mo": request.config.getoption("--slow-mo"),
    }
    env = request.config.getoption("--env")

    cfg = Config(env=env, cli_options=cli_options)
    logger.info(f"测试配置加载完成：{cfg}")
    return cfg


# ========================================
# 浏览器相关 Fixture
# ========================================

@pytest.fixture(scope="session")
def browser_instance(config):
    """
    浏览器实例（整个测试会话共享一个）
    """
    browser_name = config.browser
    headless = config.headless
    slow_mo = config.slow_mo

    logger.info(f"启动浏览器：{browser_name}（headless={headless}, slow_mo={slow_mo}）")

    with sync_playwright() as p:
        if browser_name == "chromium":
            browser_type = p.chromium
        elif browser_name == "firefox":
            browser_type = p.firefox
        else:
            browser_type = p.webkit

        browser = browser_type.launch(
            headless=headless,
            slow_mo=slow_mo,
        )

        yield browser

        browser.close()
        logger.info(f"浏览器已关闭：{browser_name}")


@pytest.fixture
def context(browser_instance, config):
    """
    浏览器上下文（每个用例独立）
    """
    context = browser_instance.new_context(
        viewport={
            "width": config.viewport_width,
            "height": config.viewport_height,
        },
        base_url=config.base_url,
    )
    yield context
    context.close()


@pytest.fixture
def page(context, config):
    """
    页面对象（每个用例独立）
    """
    page = context.new_page()
    page.set_default_timeout(config.timeout)

    yield page

    page.close()


# ========================================
# 配置相关的便捷 Fixture
# ========================================

@pytest.fixture
def base_url(config):
    """获取被测系统地址"""
    return config.base_url


# ========================================
# 测试数据 Fixture
# ========================================

@pytest.fixture
def admin_user():
    """管理员账号"""
    return {
        "username": "admin",
        "password": "admin123",
        "nickname": "管理员",
        "role": "admin",
    }


@pytest.fixture
def normal_user():
    """普通用户账号"""
    return {
        "username": "testuser",
        "password": "test123",
        "nickname": "测试用户",
        "role": "user",
    }


@pytest.fixture
def vip_user():
    """VIP 用户账号"""
    return {
        "username": "vipuser",
        "password": "vip123",
        "nickname": "VIP 用户",
        "role": "vip",
    }


# ========================================
# POM 页面对象 Fixture          ← 新增
# ========================================

@pytest.fixture
def login_page(page):
    """登录页面对象"""
    return LoginPage(page)


@pytest.fixture
def home_page(page):
    """首页页面对象"""
    return HomePage(page)


@pytest.fixture
def product_page(page):
    """商品详情页面对象"""
    return ProductPage(page)


@pytest.fixture
def cart_page(page):
    """购物车页面对象"""
    return CartPage(page)


@pytest.fixture
def order_page(page):
    """订单页面对象"""
    return OrderPage(page)


@pytest.fixture
def profile_page(page):
    """个人中心页面对象"""
    return ProfilePage(page)


# ========================================
# 截图和报告
# ========================================

@pytest.fixture(autouse=True)
def test_report(request, page):
    """
    自动应用到所有用例：
    - 记录用例开始和结束
    - 失败时自动截图
    - 附加到 Allure 报告
    """
    test_name = request.node.name
    logger.info(f"{'=' * 40}")
    logger.info(f"开始执行：{test_name}")

    yield

    # 用例执行完毕
    if request.node.rep_call and request.node.rep_call.failed:
        logger.error(f"用例失败：{test_name}")
        # 失败自动截图
        Screenshot.take(page, f"失败_{test_name}", attach_to_allure=True)
        # 附加页面信息
        try:
            AllureHelper.page_info(page)
        except Exception:
            pass
    elif request.node.rep_call and request.node.rep_call.passed:
        logger.info(f"用例通过：{test_name}")
    else:
        logger.warning(f"用例状态未知：{test_name}")

    logger.info(f"结束执行：{test_name}")


# ========================================
# Pytest Hook
# ========================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """记录用例执行结果"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ========================================
# 会话级别 Hook
# ========================================

def pytest_sessionstart(session):
    """测试会话开始时生成 Allure 配置文件"""
    try:
        from allure_config import write_categories, write_environment, write_executor
        write_categories()
        write_environment()
        write_executor()
    except Exception as e:
        logger.warning(f"生成 Allure 配置失败：{e}")


def pytest_configure(config):
    """测试会话开始时调用"""
    logger.info("=" * 60)
    logger.info("MallLite UI 自动化测试会话开始")
    logger.info(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时调用"""
    passed = session.testscollected - session.testsfailed
    total = session.testscollected
    logger.info("=" * 60)
    logger.info(f"测试会话结束")
    logger.info(f"总用例：{total}，通过：{passed}，失败：{session.testsfailed}")
    logger.info(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)