Feature: 登录功能
  作为 MallLite 的用户
  我想要通过账号密码登录系统
  以便访问个人中心和购物功能

  Background:
    Given 我在登录页面

  # ========================================
  # 正向场景
  # ========================================

  @smoke @p0
  Scenario: 管理员正常登录
    When 我输入用户名 "admin" 和密码 "admin123"
    And 我点击登录按钮
    Then 我应该成功登录并跳转到首页

  @smoke @p0
  Scenario: 普通用户正常登录
    When 我输入用户名 "testuser" 和密码 "test123"
    And 我点击登录按钮
    Then 我应该成功登录并跳转到首页

  @smoke @p0
  Scenario: VIP 用户正常登录
    When 我输入用户名 "vipuser" 和密码 "vip123"
    And 我点击登录按钮
    Then 我应该成功登录并跳转到首页

  # ========================================
  # 反向场景
  # ========================================

  @regression @p1
  Scenario: 密码错误无法登录
    When 我输入用户名 "admin" 和密码 "wrong_password"
    And 我点击登录按钮
    Then 我应该看到错误提示 "密码错误"

  @regression @p1
  Scenario: 用户名不存在无法登录
    When 我输入用户名 "nonexistent_user" 和密码 "123456"
    And 我点击登录按钮
    Then 我应该看到错误提示 "用户不存在"

  @regression @p1
  Scenario: 用户名为空无法登录
    When 我输入用户名空值和密码 "admin123"
    And 我点击登录按钮
    Then 我应该看到错误提示 "请输入用户名"

  @regression @p1
  Scenario: 密码为空无法登录
    When 我输入用户名 "admin" 和密码空值
    And 我点击登录按钮
    Then 我应看到错误提示 "请输入密码"

  # ========================================
  # 参数化场景（数据驱动）
  # ========================================

  @ddt
  Scenario Outline: 多种用户类型登录验证
    When 我输入用户名 "<username>" 和密码 "<password>"
    And 我点击登录按钮
    Then 我应该看到结果 "<result>"

    Examples:
      | username           | password      | result       |
      | admin              | admin123      | 成功         |
      | testuser           | test123       | 成功         |
      | vipuser            | vip123        | 成功         |
      | admin              | wrong         | 密码错误     |
      | nonexistent        | 123456        | 用户不存在   |
      | NONE               | admin123      | 请输入用户名 |
      | admin              | NONE          | 请输入密码   |