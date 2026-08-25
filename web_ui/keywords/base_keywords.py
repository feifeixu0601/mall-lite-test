"""
BaseKeywords - 底层通用关键字
封装浏览器基础操作，每个关键字对应一个原子操作

这些关键字直接操作 Playwright 的 page 对象，
不依赖任何页面对象类
"""

from common.logger import get_logger

logger = get_logger("base_keywords")


class BaseKeywords:
    """
    底层通用关键字类

    所有方法的第一个参数都是 page（Playwright 的 page 对象）
    方法名就是关键字名
    """

    def __init__(self, page):
        self.page = page

    # ========================================
    # 导航关键字
    # ========================================

    def navigate(self, url):
        """
        导航到指定地址

        YAML 用法：
            - keyword: navigate
              params:
                url: "/login"
        """
        logger.info(f"[关键字] 导航到：{url}")
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")

    def reload(self):
        """
        刷新当前页面

        YAML 用法：
            - keyword: reload
        """
        logger.info("[关键字] 刷新页面")
        self.page.reload()
        self.page.wait_for_load_state("domcontentloaded")

    def go_back(self):
        """
        浏览器后退

        YAML 用法：
            - keyword: go_back
        """
        logger.info("[关键字] 后退")
        self.page.go_back()

    # ========================================
    # 输入关键字
    # ========================================

    def fill(self, selector, value):
        """
        清空并输入文本

        YAML 用法：
            - keyword: fill
              params:
                selector: "#username"
                value: "admin"
        """
        logger.info(f"[关键字] 输入：{selector} → '{value}'")
        self.page.fill(selector, str(value))

    def type_text(self, selector, value, delay=50):
        """
        逐字输入（模拟真实键盘）

        YAML 用法：
            - keyword: type_text
              params:
                selector: "#search-input"
                value: "iPhone"
                delay: 100
        """
        logger.info(f"[关键字] 逐字输入：{selector} → '{value}'")
        self.page.type(selector, str(value), delay=delay)

    def clear(self, selector):
        """
        清空输入框

        YAML 用法：
            - keyword: clear
              params:
                selector: "#username"
        """
        self.page.fill(selector, "")

    # ========================================
    # 点击关键字
    # ========================================

    def click(self, selector):
        """
        点击元素

        YAML 用法：
            - keyword: click
              params:
                selector: "#login-btn"
        """
        logger.info(f"[关键字] 点击：{selector}")
        self.page.click(selector)

    def double_click(self, selector):
        """
        双击元素

        YAML 用法：
            - keyword: double_click
              params:
                selector: ".product-card"
        """
        self.page.dblclick(selector)

    def hover(self, selector):
        """
        鼠标悬停

        YAML 用法：
            - keyword: hover
              params:
                selector: ".dropdown-menu"
        """
        self.page.hover(selector)

    def check(self, selector):
        """
        勾选复选框

        YAML 用法：
            - keyword: check
              params:
                selector: "#remember"
        """
        self.page.check(selector)

    def uncheck(self, selector):
        """
        取消勾选

        YAML 用法：
            - keyword: uncheck
              params:
                selector: "#remember"
        """
        self.page.uncheck(selector)

    def select_option(self, selector, value):
        """
        下拉选择

        YAML 用法：
            - keyword: select_option
              params:
                selector: "#category"
                value: "手机"
        """
        self.page.select_option(selector, value)

    def press_key(self, selector, key):
        """
        按键

        YAML 用法：
            - keyword: press_key
              params:
                selector: "#search-input"
                key: "Enter"
        """
        self.page.press(selector, key)

    # ========================================
    # 等待关键字
    # ========================================

    def wait(self, milliseconds):
        """
        等待指定时间

        YAML 用法：
            - keyword: wait
              params:
                milliseconds: 1000
        """
        logger.info(f"[关键字] 等待 {milliseconds}ms")
        self.page.wait_for_timeout(int(milliseconds))

    def wait_for_visible(self, selector, timeout=10000):
        """
        等待元素可见

        YAML 用法：
            - keyword: wait_for_visible
              params:
                selector: "#result"
                timeout: 5000
        """
        logger.info(f"[关键字] 等待元素可见：{selector}")
        self.page.locator(selector).wait_for(state="visible", timeout=int(timeout))

    def wait_for_hidden(self, selector, timeout=10000):
        """
        等待元素消失

        YAML 用法：
            - keyword: wait_for_hidden
              params:
                selector: ".loading"
        """
        self.page.locator(selector).wait_for(state="hidden", timeout=int(timeout))

    def wait_for_url(self, pattern, timeout=10000):
        """
        等待 URL 包含指定内容

        YAML 用法：
            - keyword: wait_for_url
              params:
                pattern: "/cart"
        """
        self.page.wait_for_url(f"*{pattern}*", timeout=int(timeout))

    def wait_for_load(self, state="domcontentloaded"):
        """
        等待页面加载

        YAML 用法：
            - keyword: wait_for_load
              params:
                state: "networkidle"
        """
        self.page.wait_for_load_state(state)

    # ========================================
    # 滚动关键字
    # ========================================

    def scroll_to_bottom(self):
        """
        滚动到页面底部

        YAML 用法：
            - keyword: scroll_to_bottom
        """
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def scroll_to_top(self):
        """
        滚动到页面顶部

        YAML 用法：
            - keyword: scroll_to_top
        """
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_element(self, selector):
        """
        滚动到指定元素

        YAML 用法：
            - keyword: scroll_to_element
              params:
                selector: "#footer"
        """
        self.page.locator(selector).scroll_into_view_if_needed()

    # ========================================
    # 断言关键字
    # ========================================

    def assert_visible(self, selector, timeout=10000):
        """
        断言元素可见

        YAML 用法：
            - keyword: assert_visible
              params:
                selector: "#product-list"
        """
        logger.info(f"[断言] 元素可见：{selector}")
        self.page.locator(selector).wait_for(state="visible", timeout=int(timeout))

    def assert_hidden(self, selector, timeout=10000):
        """
        断言元素不可见

        YAML 用法：
            - keyword: assert_hidden
              params:
                selector: "#error-msg"
        """
        logger.info(f"[断言] 元素不可见：{selector}")
        self.page.locator(selector).wait_for(state="hidden", timeout=int(timeout))

    def assert_text(self, selector, expected_text):
        """
        断言元素包含文本

        YAML 用法：
            - keyword: assert_text
              params:
                selector: ".product-name"
                expected_text: "iPhone"
        """
        logger.info(f"[断言] 文本包含：{selector} → '{expected_text}'")
        actual = self.page.text_content(selector) or ""
        assert expected_text in actual, \
            f"断言失败：'{expected_text}' 不在 '{actual.strip()}' 中"

    def assert_exact_text(self, selector, expected_text):
        """
        断言元素文本完全匹配

        YAML 用法：
            - keyword: assert_exact_text
              params:
                selector: "#product-title"
                expected_text: "iPhone 15 Pro"
        """
        actual = (self.page.text_content(selector) or "").strip()
        assert actual == expected_text, \
            f"断言失败：期望 '{expected_text}'，实际 '{actual}'"

    def assert_url_contains(self, text):
        """
        断言 URL 包含文本

        YAML 用法：
            - keyword: assert_url_contains
              params:
                text: "/login"
        """
        current_url = self.page.url
        logger.info(f"[断言] URL 包含：'{text}'（当前：{current_url}）")
        assert text in current_url, \
            f"断言失败：URL '{current_url}' 不包含 '{text}'"

    def assert_url_not_contains(self, text):
        """
        断言 URL 不包含文本

        YAML 用法：
            - keyword: assert_url_not_contains
              params:
                text: "/login"
        """
        current_url = self.page.url
        assert text not in current_url, \
            f"断言失败：URL '{current_url}' 不应包含 '{text}'"

    def assert_title(self, expected_title):
        """
        断言页面标题包含文本

        YAML 用法：
            - keyword: assert_title
              params:
                expected_title: "MallLite"
        """
        actual_title = self.page.title()
        assert expected_title in actual_title, \
            f"断言失败：标题 '{actual_title}' 不包含 '{expected_title}'"

    def assert_element_count(self, selector, expected_count):
        """
        断言元素数量

        YAML 用法：
            - keyword: assert_element_count
              params:
                selector: ".product-card"
                expected_count: 8
        """
        actual = self.page.locator(selector).count()
        assert actual == int(expected_count), \
            f"断言失败：{selector} 期望 {expected_count} 个，实际 {actual} 个"

    def assert_element_count_min(self, selector, min_count):
        """
        断言元素数量至少为 N

        YAML 用法：
            - keyword: assert_element_count_min
              params:
                selector: ".product-card"
                min_count: 1
        """
        actual = self.page.locator(selector).count()
        assert actual >= int(min_count), \
            f"断言失败：{selector} 期望至少 {min_count} 个，实际 {actual} 个"

    def assert_value(self, selector, expected_value):
        """
        断言输入框的值

        YAML 用法：
            - keyword: assert_value
              params:
                selector: "#username"
                expected_value: "admin"
        """
        actual = self.page.input_value(selector)
        assert actual == str(expected_value), \
            f"断言失败：期望 '{expected_value}'，实际 '{actual}'"

    # ========================================
    # 截图关键字
    # ========================================

    def screenshot(self, name="screenshot"):
        """
        截图

        YAML 用法：
            - keyword: screenshot
              params:
                name: "登录成功后"
        """
        from common.screenshot import Screenshot
        Screenshot.take(self.page, name)