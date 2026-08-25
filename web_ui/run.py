"""
一键运行脚本
用法：
    python run.py smoke          # 运行冒烟测试
    python run.py regression     # 运行回归测试
    python run.py login          # 运行登录模块
    python run.py all            # 运行全部
    python run.py report         # 生成并打开 Allure 报告

    python run.py bdd            # 运行全部 BDD 用例
    python run.py bdd-smoke      # 运行 BDD 冒烟测试
    python run.py bdd-login      # 只运行登录 Feature
    python run.py bdd-search     # 只运行搜索 Feature
    python run.py bdd-cart       # 只运行购物车 Feature
    python run.py bdd-e2e        # 只运行端到端 Feature
    python run.py bdd-report     # 生成 BDD Allure 报告
"""

import subprocess
import sys


def run_command(cmd):
    """执行命令并打印输出"""
    import os
    print(f"\n执行命令：{' '.join(cmd)}")
    print("=" * 60)
    result = subprocess.run(cmd, cwd=".", env=os.environ.copy(), shell=True)
    return result.returncode


# ========================================
# Pytest 命令
# ========================================

def run_smoke():
    """运行冒烟测试"""
    return run_command([
        sys.executable, "-m", "pytest",
        "-m", "smoke",
        "-v",
        "--headed=false",
    ])


def run_regression():
    """运行回归测试"""
    return run_command([
        sys.executable, "-m", "pytest",
        "-m", "regression",
        "-v",
    ])


def run_module(module_name):
    """运行指定模块"""
    return run_command([
        sys.executable, "-m", "pytest",
        "-m", module_name,
        "-v",
    ])


def run_all():
    """运行全部用例"""
    return run_command([
        sys.executable, "-m", "pytest",
        "-v",
    ])


def run_all_headless():
    """无头模式运行全部（适合 CI/CD）"""
    return run_command([
        sys.executable, "-m", "pytest",
        "-v",
        "--headed=false",
    ])


def generate_report():
    """生成 Allure 报告"""
    import shutil

    if not shutil.which("allure"):
        print("Allure 未安装，请先安装：https://docs.qameta.io/allure/")
        print("  Windows: scoop install allure")
        print("  macOS: brew install allure")
        return 1

    # 先运行测试（生成数据）
    run_command([
        sys.executable, "-m", "pytest",
        "-v",
        "--alluredir=reports/allure-results",
        "--clean-alluredir",
    ])

    # 生成报告并打开
    return run_command(["allure", "serve", "reports/allure-results"])


# ========================================
# BDD 命令
# ========================================

def run_bdd_all():
    """运行全部 BDD 用例"""
    return run_command([
        "behave", "test_cases/bdd/features/",
    ])


def run_bdd_feature(feature_name):
    """运行指定 Feature"""
    feature_file = f"test_cases/bdd/features/{feature_name}.feature"
    return run_command(["behave", feature_file])


def run_bdd_smoke():
    """运行 BDD 冒烟测试"""
    return run_command([
        "behave", "test_cases/bdd/features/",
        "--tags=@smoke",
    ])


def run_bdd_report():
    """运行 BDD 并生成 Allure 报告"""
    run_command([
        "behave", "test_cases/bdd/features/",
        "-f", "allure_behave.formatter:AllureFormatter",
        "-o", "reports/allure-results",
    ])
    return run_command(["allure", "serve", "reports/allure-results"])


# ========================================
# 入口
# ========================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()

    commands = {
        # Pytest 命令
        "smoke": run_smoke,
        "regression": run_regression,
        "all": run_all,
        "headless": run_all_headless,
        "report": generate_report,
        # BDD 命令
        "bdd": run_bdd_all,
        "bdd-smoke": run_bdd_smoke,
        "bdd-login": lambda: run_bdd_feature("login"),
        "bdd-search": lambda: run_bdd_feature("search"),
        "bdd-cart": lambda: run_bdd_feature("cart"),
        "bdd-e2e": lambda: run_bdd_feature("e2e"),
        "bdd-report": run_bdd_report,
    }

    # 支持的模块名（Pytest marker）
    modules = ["login", "search", "product", "cart", "order", "e2e", "p0", "p1", "p2"]

    if command in commands:
        exit_code = commands[command]()
    elif command in modules:
        exit_code = run_module(command)
    else:
        print(f"未知命令：{command}")
        print(f"支持的命令：{', '.join(commands.keys())}")
        print(f"支持的模块：{', '.join(modules)}")
        exit_code = 1

    sys.exit(exit_code)