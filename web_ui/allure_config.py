"""
Allure 报告配置
自定义分类、环境信息、执行器信息
"""

import json
import platform
from pathlib import Path
from datetime import datetime


REPORT_DIR = Path("reports/allure-results")
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def write_categories():
    """
    自定义缺陷分类
    Allure 报告首页会按此分类统计失败原因
    """
    categories = [
        {
            "name": "元素定位失败",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*(?:locator|selector|element|定位).*"
        },
        {
            "name": "断言失败",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*(?:assert|AssertionError|断言|期望).*"
        },
        {
            "name": "超时失败",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*(?:timeout|Timeout|超时|timed out).*"
        },
        {
            "name": "页面加载失败",
            "matchedStatuses": ["failed"],
            "messageRegex": ".*(?:Navigation|load|加载|net::ERR).*"
        },
        {
            "name": "系统错误",
            "matchedStatuses": ["broken"],
            "messageRegex": ".*(?:Exception|Error|Traceback).*"
        },
        {
            "name": "未知失败",
            "matchedStatuses": ["failed"]
        }
    ]
    filepath = REPORT_DIR / "categories.json"
    filepath.write_text(json.dumps(categories, ensure_ascii=False, indent=2))
    print(f"Allure 分类配置已写入：{filepath}")


def write_environment():
    """
    环境信息
    Allure 报告的 Environment 标签页会显示此信息
    """
    env_info = [
        {"name": "Project", "value": "MallLite UI Automation"},
        {"name": "Python", "value": platform.python_version()},
        {"name": "OS", "value": f"{platform.system()} {platform.release()}"},
        {"name": "Browser", "value": "Chromium"},
        {"name": "Playwright", "value": _get_playwright_version()},
        {"name": "Pytest", "value": _get_pytest_version()},
        {"name": "Base URL", "value": "http://localhost:8000"},
        {"name": "Environment", "value": "dev"},
        {"name": "Run Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        {"name": "Executor", "value": platform.node()},
    ]
    filepath = REPORT_DIR / "environment.properties"
    lines = [f"{item['name']}={item['value']}" for item in env_info]
    filepath.write_text("\n".join(lines))
    print(f"Allure 环境信息已写入：{filepath}")


def write_executor():
    """
    执行器信息
    支持 CI/CD 环境自动识别
    """
    import os
    executor = {
        "name": "MallLite UI Automation",
        "type": "pytest",
        "buildOrder": int(datetime.now().timestamp()),
        "buildName": f"UI Test {datetime.now().strftime('%Y%m%d_%H%M')}",
    }

    # GitHub Actions 环境
    if os.environ.get("GITHUB_ACTIONS"):
        executor["name"] = "GitHub Actions"
        executor["buildName"] = os.environ.get("GITHUB_WORKFLOW", "CI")
        executor["buildOrder"] = int(os.environ.get("GITHUB_RUN_NUMBER", 0))
        executor["reportName"] = "MallLite UI Test Report"

    # Jenkins 环境
    elif os.environ.get("JENKINS_URL"):
        executor["name"] = "Jenkins"
        executor["buildName"] = os.environ.get("JOB_NAME", "UI-Test")
        executor["buildOrder"] = int(os.environ.get("BUILD_NUMBER", 0))

    filepath = REPORT_DIR / "executor.json"
    filepath.write_text(json.dumps(executor, ensure_ascii=False, indent=2))
    print(f"Allure 执行器信息已写入：{filepath}")


def _get_playwright_version():
    try:
        import playwright
        return playwright.__version__
    except Exception:
        return "unknown"


def _get_pytest_version():
    try:
        import pytest
        return pytest.__version__
    except Exception:
        return "unknown"


if __name__ == "__main__":
    write_categories()
    write_environment()
    write_executor()
    print("Allure 配置文件生成完成")