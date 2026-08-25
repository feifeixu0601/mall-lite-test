"""
LoginPage - 登录页面对象
封装登录页面的元素定位和操作
"""

import allure
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger("login_page")


class LoginPage(BasePage):
    """
    登录页面对象

    页面地址：/login

    封装的操作：
    - login(username, password)：登录
    - get_error_message()：获取错误提示
    - is_login_success()：判断是否登录成功
    - click_remember()：勾选记住密码
    """

    URL = "/login"

    # ========================================
    # 元素定位（页面上所有会用到的元素）
    # ========================================

    # 输入框
    INPUT_USERNAME = "#username"
    INPUT_PASSWORD = "#password"

    # 按钮
    BTN_LOGIN = "#login-btn"
    CHECKBOX_REMEMBER = "#remember"

    # 提示信息
    MSG_ERROR = "#error-msg"

    # 链接
    LINK_REGISTER = "a[href='/register']"

    # ========================================
    # 页面操作
    # ========================================

    def open(self):
        """
        打开登录页

        用法：
            login_page.open()
        """
        logger.info("打开登录页")
        self.navigate()

    def input_username(self, username):
        """
        输入用户名

        参数：
            username: 用户名
        """
        logger.info(f"输入用户名：{username}")
        self.fill(self.INPUT_USERNAME, username)

    def input_password(self, password):
        """
        输入密码

        参数：
            password: 密码
        """
        logger.debug("输入密码：******")
        self.fill(self.INPUT_PASSWORD, password)

    def click_login(self):
        """点击登录按钮"""
        logger.info("点击登录按钮")
        self.click(self.BTN_LOGIN)

    def click_remember(self):
        """勾选记住密码"""
        self.click(self.CHECKBOX_REMEMBER)

    def click_register_link(self):
        """点击注册链接"""
        self.click(self.LINK_REGISTER)

    # ========================================
    # 业务方法（组合操作）
    # ========================================

    def login(self, username, password, remember=False):
        """
        一站式登录

        参数：
            username: 用户名
            password: 密码
            remember: 是否记住密码（默认 False）

        用法：
            login_page.login("admin", "admin123")
        """
        logger.info(f"执行登录：用户={username}")
        self.open()
        self.input_username(username)
        self.input_password(password)
        if remember:
            self.click_remember()
        # 禁用浏览器 HTML5 验证，确保空值也能提交到后端  ← 新增
        self.page.evaluate(
            "document.querySelector('form[action=\"/login\"]').setAttribute('novalidate', '')"
        )  # ← 新增
        self.click_login()

    # ========================================
    # 结果获取
    # ========================================

    def get_error_message(self) -> str:
        """
        获取错误提示文本

        返回：
            错误提示字符串，如 "密码错误"、"用户不存在"

        用法：
            msg = login_page.get_error_message()
            assert msg == "密码错误"
        """
        self.wait_for_visible(self.MSG_ERROR)
        msg = self.get_text(self.MSG_ERROR)
        logger.info(f"错误提示：{msg}")
        return msg

    def is_error_displayed(self) -> bool:
        """判断是否显示了错误提示"""
        return self.is_visible(self.MSG_ERROR)

    def is_login_success(self) -> bool:
        """
        判断是否登录成功

        登录成功的标志：URL 不再是 /login（被重定向到首页）

        返回：
            True/False
        """
        current_url = self.get_current_url()
        success = "/login" not in current_url
        logger.info(f"登录{'成功' if success else '失败'}，当前 URL：{current_url}")
        return success

    def get_username_value(self) -> str:
        """获取当前用户名输入框的值"""
        return self.get_value(self.INPUT_USERNAME)