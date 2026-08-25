"""
MallLite 自动化测试 - 配置管理模块
支持三种配置方式，优先级：命令行 > 环境变量 > 配置文件 > 默认值
"""

import os
import yaml
from pathlib import Path
from datetime import datetime


class Config:
    """
    配置管理类

    用法：
        config = Config(env="dev")
        print(config.base_url)      # http://localhost:8000
        print(config.browser)       # chromium
        print(config.timeout)       # 10000
    """

    # 项目根目录（web_ui/）
    PROJECT_ROOT = Path(__file__).parent.parent

    # 默认配置
    DEFAULTS = {
        "base_url": "http://localhost:8000",
        "browser": "chromium",        # chromium / firefox / webkit
        "headless": True,
        "slow_mo": 0,                 # 操作间隔（毫秒），调试时设 500
        "timeout": 10000,             # 默认超时（毫秒）
        "viewport_width": 1280,
        "viewport_height": 720,
        "screenshot_on_failure": True, # 失败时自动截图
        "video_on_failure": False,     # 失败时录制视频
        "retry_count": 0,             # 失败重试次数
        "page_size": 10,              # 默认分页大小
    }

    def __init__(self, env="dev", cli_options=None):
        """
        初始化配置

        参数：
            env: 环境名称（dev / staging / prod）
            cli_options: 命令行参数字典（从 pytest 的 request.config 获取）
        """
        self.env = env
        self._cli_options = cli_options or {}
        self._env_config = self._load_env_config()
        self._build_config()

    def _load_env_config(self):
        """加载环境配置文件"""
        config_file = self.PROJECT_ROOT / "config" / "env_config.yaml"

        if not config_file.exists():
            return {}

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                all_envs = yaml.safe_load(f) or {}
            return all_envs.get(self.env, {})
        except Exception as e:
            print(f"加载环境配置失败：{e}")
            return {}

    def _build_config(self):
        """构建最终配置（按优先级合并）"""
        self._config = {}

        # 第一层：默认值
        self._config.update(self.DEFAULTS)

        # 第二层：环境配置文件
        self._config.update({k: v for k, v in self._env_config.items() if k != "description"})

        # 第三层：环境变量（格式：MALLLITE_BASE_URL）
        env_prefix = "MALLLITE_"
        for key in self.DEFAULTS:
            env_key = env_prefix + key.upper()
            env_value = os.environ.get(env_key)
            if env_value is not None:
                # 类型转换
                default_value = self.DEFAULTS[key]
                if isinstance(default_value, bool):
                    env_value = env_value.lower() in ("true", "1", "yes")
                elif isinstance(default_value, int):
                    env_value = int(env_value)
                self._config[key] = env_value

        # 第四层：命令行参数（最高优先级）
        cli_mapping = {
            "--base-url": "base_url",
            "--browser": "browser",
            "--headed": "headless",
            "--slow-mo": "slow_mo",
        }
        for cli_key, config_key in cli_mapping.items():
            cli_value = self._cli_options.get(cli_key)
            if cli_value is not None:
                if config_key == "headless":
                    self._config[config_key] = cli_value == "false"
                elif config_key == "slow_mo":
                    self._config[config_key] = int(cli_value)
                else:
                    self._config[config_key] = cli_value

    def get(self, key, default=None):
        """获取配置值"""
        return self._config.get(key, default)

    def __getattr__(self, name):
        """支持通过属性访问配置：config.base_url"""
        if name.startswith("_"):
            return super().__getattribute__(name)
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"Config 没有属性 '{name}'")

    def __repr__(self):
        env_desc = self._env_config.get("description", "")
        return f"Config(env='{self.env}', base_url='{self.base_url}', browser='{self.browser}')"

    @property
    def screenshot_dir(self):
        """截图目录"""
        path = self.PROJECT_ROOT / "reports" / "screenshots"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def report_dir(self):
        """报告目录"""
        path = self.PROJECT_ROOT / "reports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def allure_dir(self):
        """Allure 报告数据目录"""
        path = self.report_dir / "allure-results"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def log_dir(self):
        """日志目录"""
        path = self.report_dir / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def test_data_dir(self):
        """测试数据目录"""
        return self.PROJECT_ROOT / "test_data"

    def to_dict(self):
        """导出所有配置为字典"""
        return {
            "env": self.env,
            **self._config,
            "screenshot_dir": str(self.screenshot_dir),
            "report_dir": str(self.report_dir),
            "test_data_dir": str(self.test_data_dir),
        }