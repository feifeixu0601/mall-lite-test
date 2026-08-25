"""
KDT + DDT 测试引擎（增强版）
新增：
- 变量替换：${variable} 语法
- 数据源加载：data_source 字段
- 模板展开：一条用例模板 × N 组数据 = N 条用例
"""

import yaml
import json
import re
import allure
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from common.logger import get_logger
from common.data_reader import DataReader

logger = get_logger("test_engine")


@dataclass
class StepResult:
    """单步执行结果"""
    step_index: int
    keyword: str
    params: dict
    status: str  # "passed" / "failed" / "skipped"
    message: str = ""
    duration: float = 0.0


@dataclass
class CaseResult:
    """用例执行结果"""
    case_name: str
    status: str  # "passed" / "failed" / "error"
    steps: list = field(default_factory=list)
    error_message: str = ""
    duration: float = 0.0
    data_row: dict = field(default_factory=dict)  # DDT 数据行


class TestEngine:
    """
    KDT + DDT 测试引擎

    支持两种用法：
    1. 普通 KDT：直接执行 YAML 中的步骤
    2. KDT + DDT：从 data_source 加载数据，变量替换后执行
    """

    def __init__(self, page):
        self.page = page
        from keywords.keyword_registry import KeywordRegistry
        self.registry = KeywordRegistry(page)
        logger.info(f"引擎初始化完成，已注册 {self.registry.get_keyword_count()} 个关键字")

    # ========================================
    # 用例加载和展开
    # ========================================

    def load_cases(self, yaml_path):
        """
        加载 YAML 用例，支持 DDT 展开

        参数：
            yaml_path: YAML 文件路径

        返回：
            展开后的用例列表（每条数据一行一个用例）
        """
        raw_cases = self._load_yaml(yaml_path)
        expanded_cases = []

        for case in raw_cases:
            if "data_source" in case:
                # DDT 用例：从数据源展开
                data_rows = self._load_data_source(case["data_source"])
                for row in data_rows:
                    # 用每行数据展开模板
                    expanded = self._expand_case(case, row)
                    expanded_cases.append(expanded)
                logger.info(f"DDT 展开：'{case.get('name')}' × {len(data_rows)} 组数据")
            else:
                # 普通用例：直接加入
                expanded_cases.append(case)

        return expanded_cases

    def _load_data_source(self, source_path):
        """
        加载数据源文件

        参数：
            source_path: 数据文件路径（JSON / YAML / CSV）

        返回：
            数据列表（每个元素是一行数据的字典）
        """
        filepath = Path(source_path)
        if not filepath.is_absolute():
            filepath = Path(__file__).parent.parent / source_path

        if not filepath.exists():
            filepath = Path(__file__).parent.parent / "test_data" / source_path

        if not filepath.exists():
            raise FileNotFoundError(f"数据源文件不存在：{source_path}")

        suffix = filepath.suffix.lower()

        if suffix == ".json":
            data = DataReader.read_json(str(filepath))
        elif suffix in (".yaml", ".yml"):
            data = DataReader.read_yaml(str(filepath))
        elif suffix == ".csv":
            data = DataReader.read_csv(str(filepath))
        else:
            raise ValueError(f"不支持的数据源格式：{suffix}")

        if isinstance(data, dict):
            # 如果是字典，取第一个 list 类型的值
            for v in data.values():
                if isinstance(v, list):
                    return v
            return [data]

        return data

    def _expand_case(self, template, data_row):
        """
        用数据行展开用例模板

        参数：
            template: 用例模板（含 ${variable} 占位符）
            data_row: 数据行字典

        返回：
            展开后的用例字典
        """
        # 把模板序列化成 JSON 字符串，做变量替换，再解析回来
        template_str = json.dumps(template, ensure_ascii=False)

        for key, value in data_row.items():
            placeholder = "${" + key + "}"
            template_str = template_str.replace(placeholder, str(value))

        expanded = json.loads(template_str)

        # 标记数据来源
        expanded["_data_row"] = data_row
        return expanded

    def _substitute_vars(self, obj, data_row):
        """
        递归替换对象中的变量

        参数：
            obj: 任意 Python 对象（str / dict / list）
            data_row: 数据字典

        返回：
            替换后的对象
        """
        if isinstance(obj, str):
            for key, value in data_row.items():
                obj = obj.replace("${" + key + "}", str(value))
            return obj
        elif isinstance(obj, dict):
            return {k: self._substitute_vars(v, data_row) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_vars(item, data_row) for item in obj]
        return obj

    # ========================================
    # 用例执行
    # ========================================

    def run_yaml(self, yaml_path):
        """执行 YAML 文件中的所有用例（含 DDT 展开）"""
        cases = self.load_cases(yaml_path)
        logger.info(f"加载用例：{yaml_path}（展开后 {len(cases)} 条）")

        results = []
        for case in cases:
            result = self.run_case(case)
            results.append(result)

        passed = sum(1 for r in results if r.status == "passed")
        failed = sum(1 for r in results if r.status in ("failed", "error"))
        logger.info(f"执行完成：共 {len(results)} 条，通过 {passed} 条，失败 {failed} 条")

        return results

    def run_case(self, case_data):
        """执行单条用例"""
        case_name = case_data.get("name", "未命名用例")
        description = case_data.get("description", "")
        steps = case_data.get("steps", [])
        data_row = case_data.get("_data_row", {})

        logger.info(f"{'=' * 50}")
        logger.info(f"执行用例：{case_name}")

        result = CaseResult(case_name=case_name, status="passed", data_row=data_row)
        start_time = time.time()

        for i, step_data in enumerate(steps):
            step_result = self._execute_step(i + 1, step_data)
            self._attach_step_to_allure(step_result)
            result.steps.append(step_result)

            if step_result.status == "failed":
                result.status = "failed"
                result.error_message = step_result.message
                self._take_failure_screenshot(case_name)
                break

        result.duration = time.time() - start_time

        status_icon = "✅" if result.status == "passed" else "❌"
        logger.info(f"{status_icon} {case_name} → {result.status}（{result.duration:.2f}s）")

        return result

    def _execute_step(self, step_index, step_data):
        """执行单个步骤"""
        keyword_name = step_data.get("keyword")
        params = step_data.get("params", {})

        import time
        start_time = time.time()

        try:
            keyword_func = self.registry.get_keyword(keyword_name)
        except KeyError as e:
            return StepResult(
                step_index=step_index,
                keyword=keyword_name,
                params=params,
                status="failed",
                message=str(e),
                duration=time.time() - start_time,
            )

        try:
            display = f"{keyword_name}({', '.join(f'{k}={v}' for k, v in params.items())})"
            logger.info(f"  步骤 {step_index}：{display}")
            keyword_func(**params)

            return StepResult(
                step_index=step_index,
                keyword=keyword_name,
                params=params,
                status="passed",
                duration=time.time() - start_time,
            )
        except AssertionError as e:
            return StepResult(
                step_index=step_index,
                keyword=keyword_name,
                params=params,
                status="failed",
                message=f"断言失败：{e}",
                duration=time.time() - start_time,
            )
        except Exception as e:
            return StepResult(
                step_index=step_index,
                keyword=keyword_name,
                params=params,
                status="failed",
                message=f"执行异常：{type(e).__name__}: {e}",
                duration=time.time() - start_time,
            )

    # ========================================
    # 辅助方法
    # ========================================

    def _load_yaml(self, yaml_path):
        """加载 YAML 文件"""
        filepath = Path(yaml_path)
        if not filepath.is_absolute():
            filepath = Path(__file__).parent.parent / yaml_path
        if not filepath.exists():
            filepath = Path(__file__).parent.parent / "test_data" / yaml_path
        if not filepath.exists():
            raise FileNotFoundError(f"YAML 文件不存在：{yaml_path}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            return []
        if isinstance(data, dict):
            return data.get("cases", data.get("test_cases", [data]))
        return data

    def _attach_step_to_allure(self, step_result):
        """附加步骤到 Allure"""
        try:
            with allure.step(f"步骤 {step_result.step_index}: {step_result.keyword}"):
                if step_result.params:
                    allure.attach(
                        json.dumps(step_result.params, ensure_ascii=False, indent=2),
                        name="参数",
                        attachment_type=allure.attachment_type.JSON,
                    )
                if step_result.status == "failed":
                    allure.attach(
                        step_result.message,
                        name="失败原因",
                        attachment_type=allure.attachment_type.TEXT,
                    )
        except Exception:
            pass

    def _take_failure_screenshot(self, case_name):
        """失败截图"""
        try:
            from common.screenshot import Screenshot
            Screenshot.take(self.page, f"KDT失败_{case_name}", attach_to_allure=True)
        except Exception:
            pass