"""
搜索功能 Step Definitions
"""

from behave import given, when, then


@given('我在首页')
def step_open_home_page(context):
    """打开首页"""
    context.home_page.open()


@when('我搜索 "{keyword}"')
def step_search(context, keyword):
    """搜索商品"""
    context.home_page.search(keyword)


@when('我点击分类 "{category}"')
def step_click_category(context, category):
    """点击分类"""
    context.home_page.click_category(category)


@then('搜索结果应该不为空')
@when('搜索结果应该不为空')                         # ← 新增
def step_search_not_empty(context):
    """验证搜索结果不为空"""
    count = context.home_page.get_product_count()
    assert count > 0, f"搜索结果不应该为空，实际 {count} 个"


@then('搜索结果应该为空')
@when('搜索结果应该为空')                           # ← 新增
def step_search_empty(context):
    """验证搜索结果为空"""
    count = context.home_page.get_product_count()
    assert count == 0, f"搜索结果应该为空，实际 {count} 个"


@then('搜索结果应该至少有 {count:d} 个')
@when('搜索结果应该至少有 {count:d} 个')             # ← 新增
def step_search_min_count(context, count):
    """验证搜索结果数量"""
    actual = context.home_page.get_product_count()
    assert actual >= count, \
        f"期望至少 {count} 个结果，实际 {actual} 个"


@then('商品列表应该至少有 {count:d} 个')
@when('商品列表应该至少有 {count:d} 个')             # ← 新增
def step_product_min_count(context, count):
    """验证商品数量"""
    actual = context.home_page.get_product_count()
    assert actual >= count, \
        f"期望至少 {count} 个商品，实际 {actual} 个"