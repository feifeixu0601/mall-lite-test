"""
UserApi - 用户相关接口（完善版）

完善点：
1. 新增 login_and_share_session：登录并返回 session（供其他 API 共享）
2. 统一方法命名风格
"""

from api_objects.base_api import ApiClient
from common.logger import get_logger

logger = get_logger("user_api")


class UserApi(ApiClient):
    """用户接口类"""

    def login(self, username, password):
        """
        用户登录

        MallLite 使用 Session + Cookie 认证
        登录后 session 自动保存 Cookie，后续请求自动携带

        参数：
            username: 用户名
            password: 密码

        返回：
            requests.Response
        """
        logger.info(f"登录：{username}")
        return self.post("/api/login", json_data={
            "username": username,
            "password": password,
        })

    def login_and_share(self, username, password):
        """
        登录并返回 session（供其他 API 类共享）

        这是 fixture 中使用的方法：
        1. 用 UserApi 登录
        2. session 保存了 Cookie
        3. 把 session 赋给 CartApi/OrderApi
        4. 后者就能以登录状态发请求

        返回：
            当前实例的 session（已含 Cookie）

        异常：
            AssertionError: 登录失败时抛出
        """
        resp = self.login(username, password)
        data = resp.json()
        assert data["code"] == 200, f"登录失败：{data['message']}"
        logger.info(f"登录成功：{data['data']['username']}（{data['data']['role']}）")
        return self.session

    def register(self, username, password, nickname=None, phone=None, email=None):
        """
        用户注册

        参数：
            username: 用户名（必须）
            password: 密码（必须）
            nickname: 昵称（可选）
            phone: 手机号（可选）
            email: 邮箱（可选）
        """
        logger.info(f"注册：{username}")
        body = {"username": username, "password": password}
        if nickname:
            body["nickname"] = nickname
        if phone:
            body["phone"] = phone
        if email:
            body["email"] = email
        return self.post("/api/register", json_data=body)

    def get_user_info(self):
        """
        获取当前登录用户信息

        注意：MallLite 没有独立的 /api/user/info 接口
        用户信息在登录响应中返回
        如果 MallLite 后续增加了此接口，可直接使用
        """
        return self.get("/api/user/info")