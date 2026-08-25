"""
LoginKeywords - 登录业务关键字
封装登录相关的业务操作，内部使用 LoginPage 页面对象
"""

from common.logger import get_logger
from pages.login_page import LoginPage

logger = get_logger("login_keywords")


class LoginKeywords:
    """
    登录业务关键字

    每个方法对应一个业务级关键字
    内部使用 LoginPage 页面对象完成操作
    """

    def __init__(self, page):
        self.page = page
        self.login_page = LoginPage(page)

    def open_login_page(self):
        """
        打开登录页

        YAML 用法：
            - keyword: open_login_page
        """
        logger.info("[业务关键字] 打开登录页")
        self.login_page.open()

    def login(self, username, password, remember=False):
        """
        执行登录

        YAML 用法：
            - keyword: login
              params:
                username: "admin"
                password: "admin123"
        """
        logger.info(f"[业务关键字] 登录：{username}")
        self.login_page.login(username, password, remember)

    def input_username(self, username):
        """
        输入用户名

        YAML 用法：
            - keyword: input_username
              params:
                username: "admin"
        """
        self.login_page.input_username(username)

    def input_password(self, password):
        """
        输入密码

        YAML 用法：
            - keyword: input_password
              params:
                password: "admin123"
        """
        self.login_page.input_password(password)

    def click_login_button(self):
        """
        点击登录按钮

        YAML 用法：
            - keyword: click_login_button
        """
        self.login_page.click_login()

    def assert_login_success(self):
        """
        断言登录成功

        YAML 用法：
            - keyword: assert_login_success
        """
        logger.info("[业务关键字] 断言登录成功")
        assert self.login_page.is_login_success(), \
            f"登录失败，当前 URL：{self.login_page.get_current_url()}"

    def assert_login_fail(self):
        """
        断言登录失败

        YAML 用法：
            - keyword: assert_login_fail
        """
        logger.info("[业务关键字] 断言登录失败")
        assert not self.login_page.is_login_success(), \
            "不应该登录成功"

    def assert_error_message(self, expected_msg):
        """
        断言错误提示内容

        YAML 用法：
            - keyword: assert_error_message
              params:
                expected_msg: "密码错误"
        """
        actual_msg = self.login_page.get_error_message()
        assert expected_msg in actual_msg, \
            f"期望错误提示包含 '{expected_msg}'，实际为 '{actual_msg}'"