"""
购物车功能 Step Definitions
"""

from behave import given, when, then


@given('我已登录为管理员')
def step_login_as_admin(context):
    """以管理员身份登录"""
    context.login_page.login("admin", "admin123")
    assert context.login_page.is_login_success(), "管理员登录失败"
    context.home_page.open()


@given('我未登录')
def step_not_logged_in(context):
    """确保未登录状态"""
    context.context.clear_cookies()


@when('我在首页把第 {index:d} 个商品加入购物车')
def step_add_from_home(context, index):
    """从首页添加商品到购物车（index 从 1 开始）"""
    context.home_page.add_product_to_cart(index - 1)


@when('我打开商品 ID 为 {product_id:d} 的详情页')
def step_open_product_detail(context, product_id):
    """打开商品详情"""
    context.product_page.open(product_id)


@when('我点击加入购物车')
def step_add_to_cart(context):
    """在详情页加入购物车"""
    context.product_page.add_to_cart()


@when('我把商品加入购物车')
def step_add_current_product_to_cart(context):
    """把当前详情页的商品加入购物车"""
    context.product_page.add_to_cart()


@when('我打开购物车')
def step_open_cart(context):
    """打开购物车"""
    context.cart_page.open()


@when('我打开购物车并删除第 {index:d} 个商品')
def step_open_cart_and_delete(context, index):
    """打开购物车并删除商品"""
    context.cart_page.open()
    context.cart_page.delete_item(index - 1)


@when('我点击去结算')
def step_checkout(context):
    """去结算"""
    context.cart_page.checkout()


@when('我打开订单列表')
def step_open_orders(context):
    """打开订单列表"""
    context.order_page.open()


@when('我打开个人中心')
def step_open_profile(context):
    """打开个人中心"""
    context.profile_page.open()


@when('我点击第 {index:d} 个商品查看详情')
def step_click_product(context, index):
    """点击商品查看详情"""
    context.data["product_name"] = context.home_page.get_product_name(index - 1)
    context.home_page.click_product(index - 1)


# ========================================
# Then 步骤（加 @when 别名，支持 e2e.feature 的 And 链式调用）
# ========================================

@then('购物车不应该为空')
@when('购物车不应该为空')                           # ← 新增
def step_cart_not_empty(context):
    """验证购物车不为空"""
    assert not context.cart_page.is_empty(), "购物车不应该为空"


@then('购物车应该为空')
@when('购物车应该为空')                             # ← 新增
def step_cart_empty(context):
    """验证购物车为空"""
    assert context.cart_page.is_empty(), "购物车应该为空"


@then('订单列表不应该为空')
@when('订单列表不应该为空')                         # ← 新增
def step_orders_not_empty(context):
    """验证订单不为空"""
    assert not context.order_page.is_empty(), "订单列表不应该为空"


@then('我应该看到用户名为 "{username}"')
@when('我应该看到用户名为 "{username}"')             # ← 新增
def step_verify_username(context, username):
    """验证用户名"""
    actual = context.profile_page.get_username()
    assert actual == username, \
        f"用户名应为 '{username}'，实际为 '{actual}'"


@then('我应该看到角色为 "{role}"')
@when('我应该看到角色为 "{role}"')                   # ← 新增
def step_verify_role(context, role):
    """验证角色"""
    actual = context.profile_page.get_role()
    assert actual == role, \
        f"角色应为 '{role}'，实际为 '{actual}'"