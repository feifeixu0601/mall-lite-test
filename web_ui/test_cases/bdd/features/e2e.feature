Feature: 端到端购物链路
  作为 MallLite 的用户
  我想要完成从登录到下单的完整流程
  以便验证系统核心功能正常

  @smoke @p0
  Scenario: 完整购物下单流程
    Given 我已登录为管理员
    When 我搜索 "iPhone"
    And 搜索结果应该不为空
    And 我点击第 1 个商品查看详情
    And 我把商品加入购物车
    And 我打开购物车
    And 购物车不应该为空
    And 我点击去结算
    And 我打开订单列表
    And 订单列表不应该为空

  @regression @p1
  Scenario: 个人信息验证
    Given 我已登录为管理员
    When 我打开个人中心
    And 我应该看到用户名为 "admin"
    And 我应该看到角色为 "admin"