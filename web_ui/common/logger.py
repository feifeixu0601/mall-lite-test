"""
MallLite 自动化测试 - 日志模块
统一管理所有日志输出

用法：
    from common.logger import get_logger
    logger = get_logger("login_test")
    logger.info("开始执行登录测试")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 日志目录
LOG_DIR = PROJECT_ROOT / "reports" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 已创建的 logger 缓存（避免重复创建）
_loggers = {}


def get_logger(name="malllite", level=logging.DEBUG):
    """
    获取 logger 实例

    参数：
        name: logger 名称（建议用模块名，如 "login_test"、"base_page"）
        level: 日志级别

    返回：
        配置好的 logger 实例

    用法：
        logger = get_logger("test_login")
        logger.debug("详细调试信息")
        logger.info("普通信息")
        logger.warning("警告")
        logger.error("错误")
    """
    # 如果已经创建过，直接返回
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        _loggers[name] = logger
        return logger

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 终端输出（INFO 及以上）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出（DEBUG 及以上，按日期命名）
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"test_{today}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 缓存
    _loggers[name] = logger

    return logger


# 模块级默认 logger（可以直接 from common.logger import logger）
logger = get_logger("malllite")