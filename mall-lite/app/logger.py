"""
MallLite 日志配置
"""

import logging
from pathlib import Path
from datetime import datetime


def setup_logger(name="malllite", log_dir="logs"):
    """
    配置日志器：同时输出到终端和文件

    参数：
        name: 日志器名称
        log_dir: 日志文件目录

    返回：
        配置好的 logger 实例
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 日志文件按日期命名
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"{name}_{today}.log"

    # 获取 logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 终端输出（INFO 及以上）
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # 文件输出（DEBUG 及以上）
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(f"日志系统初始化完成，日志文件：{log_file}")

    return logger