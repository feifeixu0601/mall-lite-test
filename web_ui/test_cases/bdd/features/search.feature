Feature: 搜索功能
  作为 MallLite 的用户
  我想要搜索商品和按分类筛选
  以便快速找到想买的商品

  Background:
    Given 我在首页

  # ========================================
  # 关键词搜索
  # ========================================

  @smoke @p0
  Scenario: 搜索 iPhone 有结果
    When 我搜索 "iPhone"
    Then 搜索结果应该不为空

  @smoke @p0
  Scenario: 搜索 Pro 有多个结果
    When 我搜索 "Pro"
    Then 搜索结果应该至少有 2 个

  @regression @p1
  Scenario: 搜索不存在的商品无结果
    When 我搜索 "xyz_not_exist_12345"
    Then 搜索结果应该为空

  # ========================================
  # 分类筛选
  # ========================================

  @regression @p1
  Scenario: 筛选手机分类
    When 我点击分类 "手机"
    Then 商品列表应该至少有 2 个

  @regression @p1
  Scenario: 筛选笔记本分类
    When 我点击分类 "笔记本"
    Then 商品列表应该至少有 1 个

  @regression @p1
  Scenario: 筛选配件分类
    When 我点击分类 "配件"
    Then 商品列表应该至少有 2 个

  # ========================================
  # 参数化搜索
  # ========================================

  @ddt
  Scenario Outline: 关键词搜索数据驱动
    When 我搜索 "<keyword>"
    Then 搜索结果应该至少有 <min_count> 个

    Examples:
      | keyword   | min_count |
      | iPhone    | 1         |
      | Pro       | 2         |
      | 华为      | 1         |
      | AirPods   | 1         |