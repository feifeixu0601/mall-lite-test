"""
MallLite 应用入口 - 集成日志系统
"""

import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.logger import setup_logger                       # ← 新增
from app.data_store import DataStore
from app.routers import pages, api


def create_app():
    """创建 FastAPI 应用"""

    # 初始化日志                                                # ← 新增
    logger = setup_logger("malllite", log_dir="logs")         # ← 新增
    logger.info("=" * 50)                                     # ← 新增
    logger.info("MallLite 电商系统启动中...")                   # ← 新增
    logger.info("=" * 50)                                     # ← 新增

    app = FastAPI(title="MallLite", version="1.0.0", description="MallLite 电商系统")

    # 初始化数据存储
    store = DataStore("data")
    app.state.store = store
    app.state.logger = logger                                 # ← 新增

    # 挂载静态文件
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # 注册路由
    app.include_router(pages.router)
    app.include_router(api.router, tags=["API"])

    logger.info("路由注册完成")                                # ← 新增
    logger.info("MallLite 启动成功")                           # ← 新增
    logger.info("  访问地址：http://localhost:8000")           # ← 新增
    logger.info("  API 文档：http://localhost:8000/docs")     # ← 新增

    return app


app = create_app()