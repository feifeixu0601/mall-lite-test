"""
KDT + DDT 测试运行器（增强版）
支持普通 KDT 用例和 DDT 数据驱动用例
"""

import pytest
import allure
import yaml
from pathlib import Path

from engine.test_engine import TestEngine
from common.logger import get_logger

logger = get_logger("kdt_runner")

KDT_DIR = Path(__file__).parent


def collect_and_expand_yaml_cases(yaml_dir):
    """
    收集所有 YAML 用例并展开 DDT

    返回：
        [(yaml_path, case_data), ...] 展开后的用例列表
    """
    yaml_dir = Path(yaml_dir)
    all_cases = []

    for yaml_file in sorted(yaml_dir.rglob("*.yaml")):
        if "test_data" in str(yaml_file):
            continue

        try:
            # 创建临时引擎来加载和展开用例
            # 注意：这里不传 page，只用 load_cases 的展开逻辑
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                continue

            case_list = data.get("cases", data.get("test_cases", []))
            if isinstance(data, list):
                case_list = data

            for case_data in case_list:
                if "data_source" in case_data:
                    # DDT 用例：展开数据源
                    data_rows = _load_data_source_simple(case_data["data_source"])
                    for row in data_rows:
                        expanded = _expand_case_simple(case_data, row)
                        all_cases.append((str(yaml_file), expanded))
                else:
                    all_cases.append((str(yaml_file), case_data))

        except Exception as e:
            logger.error(f"解析 YAML 失败：{yaml_file}，{e}")

    return all_cases


def _load_data_source_simple(source_path):
    """加载数据源（简化版，不需要 page）"""
    from common.data_reader import DataReader

    filepath = Path(source_path)
    if not filepath.is_absolute():
        filepath = KDT_DIR.parent.parent / source_path
    if not filepath.exists():
        filepath = KDT_DIR.parent.parent / "test_data" / source_path

    suffix = filepath.suffix.lower()
    if suffix == ".json":
        data = DataReader.read_json(str(filepath))
    elif suffix in (".yaml", ".yml"):
        data = DataReader.read_yaml(str(filepath))
    elif suffix == ".csv":
        data = DataReader.read_csv(str(filepath))
    else:
        raise ValueError(f"不支持的数据格式：{suffix}")

    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v
        return [data]
    return data


def _expand_case_simple(template, data_row):
    """展开用例模板"""
    import json
    template_str = json.dumps(template, ensure_ascii=False)
    for key, value in data_row.items():
        template_str = template_str.replace("${" + key + "}", str(value))
    expanded = json.loads(template_str)
    expanded["_data_row"] = data_row
    return expanded


def yaml_case_id(case_data, yaml_path):
    """生成用例 ID"""
    case_name = case_data.get("name", "unnamed")
    folder = Path(yaml_path).parent.name
    # DDT 用例名中已包含变量替换后的文本
    return f"{folder}/{case_name}"


# 收集并展开所有用例
_all_yaml_cases = collect_and_expand_yaml_cases(KDT_DIR)


class TestKDTRunner:
    """KDT + DDT 测试运行器"""

    @pytest.mark.parametrize(
        "yaml_path, case_data",
        _all_yaml_cases,
        ids=[yaml_case_id(c, p) for p, c in _all_yaml_cases],
    )
    def test_kdt_case(self, page, yaml_path, case_data):
        """执行单条 KDT / KDT+DDT 用例"""
        case_name = case_data.get("name", "未命名")
        description = case_data.get("description", "")
        markers = case_data.get("markers", [])

        allure.dynamic.title(f"[KDT] {case_name}")
        if description:
            allure.dynamic.description(description)

        for marker in markers:
            if marker == "ddt":
                allure.dynamic.tag("ddt")
            if marker.startswith("p0"):
                allure.dynamic.severity("blocker")
            elif marker.startswith("p1"):
                allure.dynamic.severity("critical")
            elif marker.startswith("p2"):
                allure.dynamic.severity("normal")
            if marker in ("login", "search", "product", "cart", "order", "e2e"):
                allure.dynamic.feature(marker)
            if marker in ("smoke", "regression"):
                allure.dynamic.tag(marker)

        engine = TestEngine(page)
        result = engine.run_case(case_data)

        if result.status == "failed":
            pytest.fail(f"KDT 用例失败：{case_name}\n原因：{result.error_message}")