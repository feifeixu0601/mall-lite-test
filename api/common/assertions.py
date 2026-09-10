"""
接口断言工具

设计理念：
  MallLite 统一返回 HTTP 200，不能用 HTTP 状态码判断业务成败
  必须检查 JSON body 中的 code 字段

用法：
    resp = user_api.login("admin", "admin123")
    a = ApiAssertions(resp)

    a.assert_success()                    # code == 200
    a.assert_biz_fail(400)                # code == 400
    a.assert_message("登录成功")           # message 包含文本
    a.assert_has_field("data.username")   # 字段存在
    a.assert_field_value("data.role", "admin")  # 字段值
"""

from common.logger import get_logger

logger = get_logger("assertions")


class ApiAssertions:
    """接口响应断言"""

    def __init__(self, response):
        """
        参数：
            response: requests.Response 对象
        """
        self.resp = response
        self.status_code = response.status_code
        try:
            self.body = response.json()
        except Exception:
            self.body = {}
        self.elapsed = response.elapsed.total_seconds()

    # ========================================
    # 业务状态码断言（核心）
    # ========================================

    def assert_success(self):
        """
        断言业务成功

        对 MallLite 来说就是 code == 200
        同时验证 HTTP 状态码也是 200（以防万一）
        """
        assert self.status_code == 200, \
            f"HTTP 状态码期望 200，实际 {self.status_code}"
        code = self.body.get("code")
        assert code == 200, \
            f"业务码期望 200，实际 {code}，消息：{self.body.get('message')}"
        logger.info("  ✓ 业务成功 (code=200)")
        return self

    def assert_biz_fail(self, expected_code=None):
        """
        断言业务失败

        参数：
            expected_code: 期望的 code 值（可选）
                不传 → 只要 code != 200 就算通过
                传值 → code 必须等于指定值

        用法：
            a.assert_biz_fail()      # 任意失败
            a.assert_biz_fail(400)   # code 必须是 400
            a.assert_biz_fail(401)   # code 必须是 401
        """
        code = self.body.get("code")
        assert code != 200, "接口不应该成功"
        if expected_code is not None:
            assert code == expected_code, \
                f"业务码期望 {expected_code}，实际 {code}"
        logger.info(f"  ✓ 业务失败 (code={code})")
        return self

    def assert_code(self, expected_code):
        """
        断言业务状态码等于指定值

        用法：
            a.assert_code(200)   # 成功
            a.assert_code(401)   # 未登录
            a.assert_code(400)   # 参数错误
        """
        actual = self.body.get("code")
        assert actual == expected_code, \
            f"code 期望 {expected_code}，实际 {actual}"
        logger.info(f"  ✓ code={expected_code}")
        return self

    # ========================================
    # 消息断言
    # ========================================

    def assert_message(self, text):
        """
        断言响应消息包含指定文本

        用法：
            a.assert_message("登录成功")
            a.assert_message("密码错误")
        """
        msg = self.body.get("message", "")
        assert text in msg, f"消息期望包含 '{text}'，实际为 '{msg}'"
        return self

    # ========================================
    # 字段断言
    # ========================================

    def assert_has_field(self, path):
        """
        断言字段存在

        参数：
            path: 用 . 分隔的字段路径

        用法：
            a.assert_has_field("data.username")
            a.assert_has_field("data.items")
        """
        value = self._navigate(path)
        assert value is not None, f"字段 '{path}' 不存在或为 None"
        return self

    def assert_field_value(self, path, expected):
        """断言字段值等于期望值"""
        actual = self._navigate(path)
        assert actual == expected, \
            f"字段 '{path}' 期望 {expected}，实际 {actual}"
        return self

    def assert_field_contains(self, path, text):
        """断言字段值包含指定文本"""
        actual = self._navigate(path)
        assert text in str(actual), \
            f"字段 '{path}' 期望包含 '{text}'，实际为 '{actual}'"
        return self

    def assert_field_type(self, path, expected_type):
        """
        断言字段类型

        参数：
            expected_type: 类型或类型元组

        用法：
            a.assert_field_type("data.items", list)
            a.assert_field_type("data.price", (int, float))
        """
        value = self._navigate(path)
        assert isinstance(value, expected_type), \
            f"字段 '{path}' 类型不匹配：期望 {expected_type}，实际 {type(value)}"
        return self

    def assert_field_gt(self, path, min_value):
        """断言字段值大于某个值"""
        value = self._navigate(path)
        assert value > min_value, \
            f"字段 '{path}' 期望 > {min_value}，实际 {value}"
        return self

    # ========================================
    # 列表断言
    # ========================================

    def assert_list_not_empty(self, path):
        """断言列表字段不为空"""
        value = self._navigate(path)
        assert isinstance(value, list) and len(value) > 0, \
            f"列表 '{path}' 应该不为空"
        return self

    def assert_list_min_length(self, path, min_len):
        """断言列表最少有 N 个元素"""
        value = self._navigate(path)
        assert len(value) >= min_len, \
            f"列表 '{path}' 期望至少 {min_len} 个，实际 {len(value)}"
        return self

    # ========================================
    # 响应时间
    # ========================================

    def assert_response_time(self, max_seconds):
        """断言响应时间"""
        assert self.elapsed <= max_seconds, \
            f"响应时间期望 <= {max_seconds}s，实际 {self.elapsed:.3f}s"
        return self

    # ========================================
    # 数据获取
    # ========================================

    def get_data(self):
        """获取 data 字段"""
        return self.body.get("data")

    def get_field(self, path):
        """获取指定字段的值"""
        return self._navigate(path)

    def _navigate(self, path):
        """
        按路径导航到 JSON 中的某个字段

        例如 path="data.items" 相当于 body["data"]["items"]
        """
        parts = path.split(".")
        current = self.body
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise KeyError(f"字段 '{path}' 不存在（断在 '{part}'）")
        return current

    # 在 ApiAssertions 类中追加

    def assert_schema(self, schema_name):
        """
        断言响应体符合 JSON Schema

        用法：
            assert_api(resp).assert_success().assert_schema("login")
        """
        from common.schemas import validate_schema
        validate_schema(self.body, schema_name)
        logger.info(f"  ✓ Schema 校验通过：{schema_name}")
        return self