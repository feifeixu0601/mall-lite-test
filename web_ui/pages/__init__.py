"""
页面对象层
统一导出所有页面对象
"""

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.order_page import OrderPage
from pages.profile_page import ProfilePage

__all__ = [
    "BasePage",
    "LoginPage",
    "HomePage",
    "ProductPage",
    "CartPage",
    "OrderPage",
    "ProfilePage",
]