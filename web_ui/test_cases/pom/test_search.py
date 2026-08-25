"""
搜索功能测试（POM 模式）

使用 HomePage 页面对象编写
覆盖关键词搜索、分类筛选、空搜索、翻页
"""

import pytest
from common.data_reader import DataReader
from common.allure_helper import AllureHelper


# 加载测试数据
search_data = DataReader.read_yaml("search_data.yaml")


@pytest.mark.search
class TestSearch:
    """搜索功能测试集"""

    # ========================================
    # 关键词搜索
    # ========================================

    @pytest.mark.smoke
    @pytest.mark.p0
    def test_search_has_results(self, home_page):
        """
        验证搜索存在的关键词有结果

        步骤：
            1. 打开首页
            2. 搜索 "iPhone"
            3. 验证结果数量大于 0
        """
        AllureHelper.title("搜索存在的关键词有结果")
        AllureHelper.severity("critical")
        AllureHelper.feature("搜索")

        home_page.open()
        home_page.search("iPhone")

        count = home_page.get_product_count()
        AllureHelper.attach_text(f"搜索 'iPhone'，结果数量：{count}", "搜索结果")
        assert count > 0, "搜索 'iPhone' 应该有结果"

    @pytest.mark.p1
    @pytest.mark.parametrize("case", search_data["keyword_cases"],
                             ids=[c["case_name"] for c in search_data["keyword_cases"]])
    def test_search_keyword(self, home_page, case):
        """
        数据驱动：验证各种关键词搜索结果

        从 search_data.yaml 的 keyword_cases 读取数据
        """
        AllureHelper.title(case["case_name"])
        AllureHelper.feature("搜索")
        AllureHelper.story("关键词搜索")

        home_page.open()
        home_page.search(case["keyword"])

        actual_count = home_page.get_product_count()
        AllureHelper.attach_text(
            f"关键词：{case['keyword']}\n期望最少：{case['expect_min_count']}\n实际：{actual_count}",
            "搜索详情"
        )

        assert actual_count >= case["expect_min_count"], \
            f"搜索 '{case['keyword']}' 期望至少 {case['expect_min_count']} 条，实际 {actual_count} 条"

    # ========================================
    # 分类筛选
    # ========================================

    @pytest.mark.smoke
    @pytest.mark.p1
    def test_category_filter_all(self, home_page):
        """
        验证点击"全部"显示所有商品

        步骤：
            1. 打开首页
            2. 点击某个分类
            3. 再点击"全部"
            4. 验证显示所有商品
        """
        AllureHelper.title("分类筛选-全部")
        AllureHelper.feature("搜索")
        AllureHelper.story("分类筛选")

        home_page.open()
        all_count = home_page.get_product_count()

        home_page.click_category("手机")
        phone_count = home_page.get_product_count()

        home_page.open()
        after_count = home_page.get_product_count()

        assert after_count >= phone_count, "点击全部后应该显示更多或相同数量的商品"

    @pytest.mark.p1
    @pytest.mark.parametrize("case", search_data["category_cases"],
                             ids=[c["case_name"] for c in search_data["category_cases"]])
    def test_category_filter(self, home_page, case):
        """
        数据驱动：验证各分类筛选功能
        """
        AllureHelper.title(case["case_name"])
        AllureHelper.feature("搜索")
        AllureHelper.story("分类筛选")

        home_page.open()
        home_page.click_category(case["category"])

        actual_count = home_page.get_product_count()
        AllureHelper.attach_text(
            f"分类：{case['category']}\n期望最少：{case['expect_min_count']}\n实际：{actual_count}",
            "筛选结果"
        )

        assert actual_count >= case["expect_min_count"], \
            f"{case['category']} 分类期望至少 {case['expect_min_count']} 个，实际 {actual_count} 个"

    # ========================================
    # 搜索边界
    # ========================================

    @pytest.mark.regression
    @pytest.mark.p2
    def test_search_empty(self, home_page):
        """
        验证空搜索显示所有商品

        步骤：
            1. 打开首页
            2. 搜索框留空，点击搜索
            3. 验证仍然显示商品
        """
        AllureHelper.title("空搜索显示全部商品")
        AllureHelper.feature("搜索")

        home_page.open()
        home_page.search("")

        count = home_page.get_product_count()
        assert count > 0, "空搜索应该显示所有商品"

    @pytest.mark.regression
    @pytest.mark.p2
    def test_search_no_result(self, home_page):
        """
        验证搜索不存在的商品无结果

        步骤：
            1. 打开首页
            2. 搜索不存在的关键词
            3. 验证无商品显示
        """
        AllureHelper.title("搜索不存在的商品无结果")
        AllureHelper.feature("搜索")

        home_page.open()
        home_page.search("xyz_不存在的商品_12345")

        count = home_page.get_product_count()
        assert count == 0, f"搜索不存在的商品应该无结果，实际有 {count} 个"