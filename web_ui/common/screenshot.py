"""
MallLite 自动化测试 - 截图工具
统一管理截图的命名、存储和报告附加

用法：
    from common.screenshot import Screenshot

    # 截取全页面
    Screenshot.take(page, "登录成功后")

    # 截取指定元素
    Screenshot.element(page.locator("#product-list"), "商品列表")

    # 截取并附加到 Allure
    Screenshot.take(page, "失败现场", attach_to_allure=True)
"""

from datetime import datetime
from pathlib import Path
from common.logger import get_logger

logger = get_logger("screenshot")

# 截图目录
PROJECT_ROOT = Path(__file__).parent.parent
SCREENSHOT_DIR = PROJECT_ROOT / "reports" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


class Screenshot:
    """截图工具类"""

    @staticmethod
    def take(page, name="screenshot", attach_to_allure=True):
        """
        对当前页面截图

        参数：
            page: Playwright 的 page 对象
            name: 截图描述（会出现在文件名中）
            attach_to_allure: 是否附加到 Allure 报告

        返回：
            截图文件路径（Path 对象）
        """
        # 生成文件名：描述_时间戳.png
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        # 清理文件名中的特殊字符
        safe_name = name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        filename = f"{safe_name}_{timestamp}.png"
        filepath = SCREENSHOT_DIR / filename

        try:
            page.screenshot(path=str(filepath), full_page=True)
            logger.info(f"截图已保存：{filepath.name}")

            # 附加到 Allure 报告
            if attach_to_allure:
                Screenshot._attach_to_allure(filepath, name)

            return filepath
        except Exception as e:
            logger.error(f"截图失败：{e}")
            return None

    @staticmethod
    def element(locator, name="element", attach_to_allure=True):
        """
        对指定元素截图

        参数：
            locator: Playwright 的 locator 对象
            name: 截图描述
            attach_to_allure: 是否附加到 Allure 报告

        返回：
            截图文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        safe_name = name.replace(" ", "_").replace("/", "_")
        filename = f"elem_{safe_name}_{timestamp}.png"
        filepath = SCREENSHOT_DIR / filename

        try:
            locator.screenshot(path=str(filepath))
            logger.info(f"元素截图已保存：{filepath.name}")

            if attach_to_allure:
                Screenshot._attach_to_allure(filepath, name)

            return filepath
        except Exception as e:
            logger.error(f"元素截图失败：{e}")
            return None

    @staticmethod
    def _attach_to_allure(filepath, name):
        """将截图附加到 Allure 报告"""
        try:
            import allure
            allure.attach.file(
                str(filepath),
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
        except ImportError:
            pass  # Allure 未安装时忽略
        except Exception as e:
            logger.debug(f"附加到 Allure 失败：{e}")