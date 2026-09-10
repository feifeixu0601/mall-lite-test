"""
ApiClient 基类（增强版）

增强点：
1. 自动重试（5xx 错误自动重试 2 次，带退避间隔）
2. 可配置超时（默认 10 秒，单个接口可覆盖）
3. Session 安全管理（确保异常时也能关闭）
4. 统一的请求/响应日志格式
"""

import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from common.logger import get_logger

logger = get_logger("api_client")


class ApiClient:
    """
    接口请求基类

    所有业务 API 类（UserApi、CartApi 等）继承此类

    用法：
        api = ApiClient("http://localhost:8000")
        resp = api.get("/api/products")
        resp = api.post("/api/login", json_data={"username": "admin", "password": "123"})
        api.close()
    """

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        # 默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        # 配置自动重试策略
        # 只对 GET/PUT/DELETE（幂等请求）重试，POST 不自动重试（避免重复创建）
        retry_strategy = Retry(
            total=2,                          # 最多重试 2 次
            backoff_factor=0.5,               # 退避间隔：第 1 次等 0.5s，第 2 次等 1s
            status_forcelist=[500, 502, 503, 504],  # 这些 HTTP 状态码触发重试
            allowed_methods=["GET", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 请求统计
        self._request_count = 0
        self._fail_count = 0

    # ========================================
    # HTTP 请求方法
    # ========================================

    def get(self, path, params=None, timeout=None):
        """
        GET 请求

        参数：
            path: 接口路径
            params: URL 参数
            timeout: 超时秒数（None 用默认 10 秒）
        """
        return self._request("GET", path, params=params, timeout=timeout)

    def post(self, path, json_data=None, timeout=None):
        """POST 请求"""
        return self._request("POST", path, json_data=json_data, timeout=timeout)

    def put(self, path, json_data=None, timeout=None):
        """PUT 请求"""
        return self._request("PUT", path, json_data=json_data, timeout=timeout)

    def delete(self, path, timeout=None):
        """DELETE 请求"""
        return self._request("DELETE", path, timeout=timeout)

    def _request(self, method, path, json_data=None, params=None, timeout=None):
        """
        发送请求的核心方法

        职责：
        1. 拼接完整 URL
        2. 发送请求（自动重试由 urllib3 Retry 处理）
        3. 记录请求/响应日志
        4. 更新请求统计
        """
        url = f"{self.base_url}{path}"
        self._request_count += 1
        req_timeout = timeout or 10

        # ===== 请求日志 =====
        logger.info(f">>> {method} {url}")
        if params:
            logger.info(f"    Params: {json.dumps(params, ensure_ascii=False)}")
        if json_data:
            logger.info(f"    Body: {json.dumps(json_data, ensure_ascii=False)}")

        # ===== 发送请求 =====
        start = time.time()
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=req_timeout,
            )
            elapsed = time.time() - start

            # ===== 响应日志 =====
            logger.info(f"<<< {response.status_code} ({elapsed:.3f}s)")
            try:
                body = response.json()
                logger.info(f"    {json.dumps(body, ensure_ascii=False)[:300]}")
            except Exception:
                logger.info(f"    {response.text[:200]}")

            # 统计失败
            if response.status_code >= 400:
                self._fail_count += 1

            return response

        except requests.exceptions.ConnectionError:
            self._fail_count += 1
            logger.error(f"连接失败：{url}（请确认 MallLite 是否启动）")
            raise
        except requests.exceptions.Timeout:
            self._fail_count += 1
            logger.error(f"请求超时：{url}（{req_timeout}s）")
            raise
        except Exception as e:
            self._fail_count += 1
            logger.error(f"请求异常：{e}")
            raise

    # ========================================
    # 会话管理
    # ========================================

    def close(self):
        """关闭 session"""
        self.session.close()
        logger.debug(f"Session 已关闭（请求 {self._request_count} 次，失败 {self._fail_count} 次）")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()