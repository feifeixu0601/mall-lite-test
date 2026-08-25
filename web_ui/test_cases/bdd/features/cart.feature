Feature: 购物车功能
  作为已登录的用户
  我想要把商品加入购物车并管理
  以便统一结算购买

  Background:
    Given 我已登录为管理员

  @smoke @p0
  Scenario: 从首页添加商品到购物车
    When 我在首页把第 1 个商品加入购物车
    And 我打开购物车
    Then 购物车不应该为空

  @smoke @p0
  Scenario: 从详情页添加商品到购物车
    When 我打开商品 ID 为 1 的详情页
    And 我点击加入购物车
    And 我打开购物车
    Then 购物车不应该为空

  @regression @p1
  Scenario: 删除购物车商品
    When 我在首页把第 1 个商品加入购物车
    When 我打开购物车并删除第 1 个商品
    Then 购物车应该为空

  @regression @p1
  Scenario: 未登录访问购物车为空
    Given 我未登录
    When 我打开购物车
    Then 购物车应该为空