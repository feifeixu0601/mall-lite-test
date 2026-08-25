"""
BasePage - 页面对象基类
封装 Playwright 通用操作，所有页面对象都继承此类

设计原则：
1. 封装通用操作（点击、输入、等待、截图等）
2. 不包含任何业务逻辑
3. 每个方法职责单一
4. 失败时提供清晰的错误信息
"""

import allure
from playwright.sync_api import Page, Locator, expect
from common.logger import get_logger
from common.screenshot import Screenshot

logger = get_logger("base_page")


class BasePage:
    """
    页面对象基类

    所有页面对象（LoginPage、HomePage 等）都继承此类
    提供通用的元素操作、等待、验证、截图方法
    """

    # 页面 URL（子类覆盖）
    URL = ""

    def __init__(self, page: Page):
        """
        初始化

        参数：
            page: Playwright 的 page 对象
        """
        self.page = page

    # ========================================
    # 页面导航
    # ========================================

    def navigate(self, url=None):
        """
        导航到页面

        参数：
            url: 页面地址（不传则使用子类定义的 URL）
        """
        target = url or self.URL
        logger.info(f"导航到：{target}")
        self.page.goto(target)
        self.wait_for_load()

    def wait_for_load(self, state="domcontentloaded"):
        """
        等待页面加载完成

        参数：
            state: 加载状态
                   "load" - 等待所有资源加载完成
                   "domcontentloaded" - 等待 DOM 加载完成
                   "networkidle" - 等待网络空闲
        """
        self.page.wait_for_load_state(state)

    def reload(self):
        """刷新页面"""
        logger.info("刷新页面")
        self.page.reload()
        self.wait_for_load()

    def go_back(self):
        """后退"""
        self.page.go_back()

    def get_current_url(self):
        """获取当前 URL"""
        return self.page.url

    def get_title(self):
        """获取页面标题"""
        return self.page.title()

    # ========================================
    # 元素定位（核心）
    # ========================================

    def find(self, selector) -> Locator:
        """
        查找元素

        参数：
            selector: CSS 选择器或其他定位方式

        返回：
            Locator 对象

        说明：
            Playwright 的 Locator 是惰性的，调用 find 时不会立即查找元素，
            而是在执行操作（click、fill 等）时才真正去查找
        """
        return self.page.locator(selector)

    def find_by_text(self, text) -> Locator:
        """通过文本内容定位元素"""
        return self.page.get_by_text(text)

    def find_by_role(self, role, name=None) -> Locator:
        """通过角色定位元素"""
        return self.page.get_by_role(role, name=name)

    def find_by_placeholder(self, text) -> Locator:
        """通过 placeholder 定位元素"""
        return self.page.get_by_placeholder(text)

    # ========================================
    # 元素操作
    # ========================================

    def click(self, selector):
        """
        点击元素

        参数：
            selector: 元素选择器
        """
        logger.debug(f"点击：{selector}")
        self.page.click(selector)

    def double_click(self, selector):
        """双击元素"""
        logger.debug(f"双击：{selector}")
        self.page.dblclick(selector)

    def fill(self, selector, text):
        """
        清空输入框并输入文本

        参数：
            selector: 输入框选择器
            text: 要输入的文本
        """
        logger.debug(f"输入：{selector} → '{text}'")
        self.page.fill(selector, str(text))

    def type_text(self, selector, text, delay=50):
        """
        逐字输入（模拟真实键盘输入）

        参数：
            selector: 输入框选择器
            text: 要输入的文本
            delay: 每个字符的间隔（毫秒）
        """
        logger.debug(f"逐字输入：{selector} → '{text}'")
        self.page.type(selector, str(text), delay=delay)

    def clear(self, selector):
        """清空输入框"""
        self.page.fill(selector, "")

    def get_text(self, selector) -> str:
        """
        获取元素文本

        参数：
            selector: 元素选择器

        返回：
            元素的文本内容
        """
        text = self.page.text_content(selector) or ""
        logger.debug(f"获取文本：{selector} → '{text.strip()}'")
        return text.strip()

    def get_inner_text(self, selector) -> str:
        """获取元素的 innerText（包含隐藏元素的文本不返回）"""
        text = self.page.inner_text(selector) or ""
        return text.strip()

    def get_value(self, selector) -> str:
        """获取输入框的值"""
        return self.page.input_value(selector)

    def get_attribute(self, selector, attr_name) -> str:
        """
        获取元素属性值

        参数：
            selector: 元素选择器
            attr_name: 属性名

        返回：
            属性值字符串
        """
        value = self.page.get_attribute(selector, attr_name)
        logger.debug(f"获取属性：{selector}.{attr_name} → '{value}'")
        return value

    def select_option(self, selector, value):
        """下拉选择框选择"""
        logger.debug(f"下拉选择：{selector} → {value}")
        self.page.select_option(selector, value)

    def check(self, selector):
        """勾选复选框"""
        self.page.check(selector)

    def uncheck(self, selector):
        """取消勾选"""
        self.page.uncheck(selector)

    def is_checked(self, selector) -> bool:
        """判断复选框是否勾选"""
        return self.page.is_checked(selector)

    def hover(self, selector):
        """鼠标悬停"""
        logger.debug(f"悬停：{selector}")
        self.page.hover(selector)

    def press_key(self, selector, key):
        """
        按键

        参数：
            selector: 元素选择器
            key: 按键名，如 "Enter"、"Escape"、"Tab"
        """
        logger.debug(f"按键：{selector} → {key}")
        self.page.press(selector, key)

    def upload_file(self, selector, file_path):
        """上传文件"""
        self.page.set_input_files(selector, file_path)

    # ========================================
    # 元素状态判断
    # ========================================

    def is_visible(self, selector, timeout=3000) -> bool:
        """
        判断元素是否可见

        参数：
            selector: 元素选择器
            timeout: 超时时间（毫秒），0 表示不等待

        返回：
            True/False
        """
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_hidden(self, selector, timeout=3000) -> bool:
        """判断元素是否隐藏"""
        try:
            self.page.locator(selector).wait_for(state="hidden", timeout=timeout)
            return True
        except Exception:
            return False

    def element_exists(self, selector) -> bool:
        """
        判断元素是否存在（不要求可见）

        返回：
            True/False
        """
        return self.page.locator(selector).count() > 0

    def get_element_count(self, selector) -> int:
        """获取元素数量"""
        return self.page.locator(selector).count()

    # ========================================
    # 等待操作
    # ========================================

    def wait_for_visible(self, selector, timeout=None):
        """
        等待元素可见

        参数：
            selector: 元素选择器
            timeout: 超时时间（毫秒），None 使用默认超时
        """
        logger.debug(f"等待元素可见：{selector}")
        self.page.locator(selector).wait_for(state="visible", timeout=timeout)

    def wait_for_hidden(self, selector, timeout=None):
        """等待元素消失"""
        logger.debug(f"等待元素消失：{selector}")
        self.page.locator(selector).wait_for(state="hidden", timeout=timeout)

    def wait_for_url(self, pattern, timeout=None):
        """
        等待 URL 包含指定内容

        参数：
            pattern: URL 中要包含的内容
            timeout: 超时时间
        """
        logger.debug(f"等待 URL 包含：{pattern}")
        self.page.wait_for_url(f"**{pattern}**", timeout=timeout)

    def wait_for_timeout(self, ms):
        """
        等待指定时间（尽量少用，优先用智能等待）

        参数：
            ms: 等待毫秒数
        """
        logger.debug(f"等待 {ms}ms")
        self.page.wait_for_timeout(ms)

    # ========================================
    # 滚动操作
    # ========================================

    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_element(self, selector):
        """滚动到指定元素"""
        self.page.locator(selector).scroll_into_view_if_needed()

    # ========================================
    # 截图和断言辅助
    # ========================================

    def take_screenshot(self, name="screenshot"):
        """
        截图

        参数：
            name: 截图描述
        """
        return Screenshot.take(self.page, name)

    def expect_visible(self, selector, timeout=None):
        """
        断言元素可见

        参数：
            selector: 元素选择器
            timeout: 超时时间
        """
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    def expect_hidden(self, selector, timeout=None):
        """断言元素隐藏"""
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)

    def expect_text(self, selector, expected_text, timeout=None):
        """断言元素包含文本"""
        expect(self.page.locator(selector)).to_contain_text(expected_text, timeout=timeout)

    def expect_exact_text(self, selector, expected_text, timeout=None):
        """断言元素文本完全匹配"""
        expect(self.page.locator(selector)).to_have_text(expected_text, timeout=timeout)

    def expect_url_contains(self, pattern, timeout=None):
        """断言 URL 包含内容"""
        expect(self.page).to_have_url(f"*{pattern}*", timeout=timeout)

    def expect_title(self, expected_title, timeout=None):
        """断言页面标题"""
        expect(self.page).to_have_title(f"*{expected_title}*", timeout=timeout)

    def expect_value(self, selector, expected_value, timeout=None):
        """断言输入框的值"""
        expect(self.page.locator(selector)).to_have_value(expected_value, timeout=timeout)

    def expect_count(self, selector, expected_count, timeout=None):
        """断言元素数量"""
        expect(self.page.locator(selector)).to_have_count(expected_count, timeout=timeout)

    # ========================================
    # 浏览器信息
    # ========================================

    def get_console_messages(self):
        """获取控制台消息（需要在页面加载前注册监听）"""
        messages = []
        self.page.on("console", lambda msg: messages.append(msg))
        return messages

    def get_cookies(self):
        """获取当前页面的所有 Cookie"""
        return self.page.context.cookies()

    def add_cookie(self, name, value):
        """添加 Cookie"""
        self.page.context.add_cookies([{"name": name, "value": value, "url": self.page.url}])

    def clear_cookies(self):
        """清除所有 Cookie"""
        self.page.context.clear_cookies()