"""
MallLite 启动脚本
用法：python run.py
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("  MallLite 电商系统启动中...")
    print("  访问地址：http://localhost:8000")
    print("  API 文档：http://localhost:8000/docs")
    print("=" * 50)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )