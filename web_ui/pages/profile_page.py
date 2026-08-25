"""
ProfilePage - 个人中心页面对象
"""

import allure
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger("profile_page")


class ProfilePage(BasePage):
    """
    个人中心页面对象

    页面地址：/profile
    """

    URL = "/profile"

    # ========================================
    # 元素定位
    # ========================================

    CARD_PROFILE = "#profile-card"
    TEXT_USERNAME = "#profile-username"
    TEXT_NICKNAME = "#profile-nickname"
    TEXT_PHONE = "#profile-phone"
    TEXT_EMAIL = "#profile-email"
    TEXT_ROLE = "#profile-role"
    BTN_LOGOUT = "#logout-btn"
    DIV_LOGIN_PROMPT = ".login-prompt"

    # ========================================
    # 页面操作
    # ========================================

    def open(self):
        """打开个人中心"""
        logger.info("打开个人中心")
        self.navigate()

    def get_username(self) -> str:
        """获取用户名"""
        return self.get_text(self.TEXT_USERNAME)

    def get_nickname(self) -> str:
        """获取昵称"""
        return self.get_text(self.TEXT_NICKNAME)

    def get_role(self) -> str:
        """获取角色"""
        return self.get_text(self.TEXT_ROLE)

    def click_logout(self):
        """点击退出登录"""
        logger.info("退出登录")
        self.click(self.BTN_LOGOUT)

    def is_logged_in(self) -> bool:
        """判断是否已登录"""
        return self.is_visible(self.CARD_PROFILE)

    def is_login_prompt_displayed(self) -> bool:
        """是否显示登录提示（未登录状态）"""
        return self.is_visible(self.DIV_LOGIN_PROMPT)