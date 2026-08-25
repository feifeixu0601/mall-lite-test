"""
第一个 Playwright 测试用例
验证 MallLite 首页能正常访问
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.p0
def test_homepage_title(page: Page):
    """
    验证首页标题
    步骤：
        1. 打开首页
        2. 验证页面标题包含 MallLite
    """
    page.goto("http://localhost:8000")
    assert "MallLite" in page.title()


@pytest.mark.smoke
@pytest.mark.p0
def test_homepage_has_products(page: Page):
    """
    验证首页有商品展示
    步骤：
        1. 打开首页
        2. 验证商品列表区域存在
        3. 验证至少有一个商品卡片
    """
    page.goto("http://localhost:8000")

    # 验证商品列表容器存在
    product_list = page.locator("#product-list")
    expect(product_list).to_be_visible()

    # 验证至少有一个商品卡片
    product_cards = page.locator(".product-card")
    assert product_cards.count() > 0, "首页没有展示任何商品"


@pytest.mark.regression
@pytest.mark.search
def test_homepage_has_search(page: Page):
    """
    验证首页有搜索框
    步骤：
        1. 打开首页
        2. 验证搜索输入框存在
        3. 验证搜索按钮存在
    """
    page.goto("http://localhost:8000")

    search_input = page.locator("#search-input")
    expect(search_input).to_be_visible()

    search_btn = page.locator("#search-btn")
    expect(search_btn).to_be_visible()


@pytest.mark.regression
def test_homepage_has_category_nav(page: Page):
    """
    验证首页有分类导航
    步骤：
        1. 打开首页
        2. 验证分类导航存在
        3. 验证至少有 4 个分类
    """
    page.goto("http://localhost:8000")

    category_nav = page.locator("#category-nav")
    expect(category_nav).to_be_visible()

    category_links = page.locator(".category-link")
    assert category_links.count() >= 4, f"分类数量不足，期望至少 4 个，实际 {category_links.count()} 个"