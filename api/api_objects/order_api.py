"""
OrderApi - 订单相关接口（完善版）

关键点（来自探针脚本验证）：
  - 订单没有 id 字段，查详情用 order_no
  - 订单列表字段：order_no, user_id, items, total_price, status, created_at, updated_at
  - 空购物车创建订单：code=400, message=购物车为空
"""

from api_objects.base_api import ApiClient
from common.logger import get_logger

logger = get_logger("order_api")


class OrderApi(ApiClient):

    def create_order(self):
        """
        创建订单（从购物车结算）

        前提：购物车中必须有商品
        否则返回：code=400, message=购物车为空
        """
        logger.info("创建订单")
        return self.post("/api/orders")

    def get_orders(self, page=1, page_size=10):
        """
        获取订单列表

        返回字段：items 中每个元素包含
          order_no, user_id, items, total_price, status, created_at, updated_at
        """
        return self.get("/api/orders", params={"page": page, "page_size": page_size})

    def get_order(self, order_no):
        """
        获取订单详情

        参数：
            order_no: 订单号（如 "ORD20260827-000003"）

        注意：这里用 order_no 查询，不是 id
        """
        return self.get(f"/api/orders/{order_no}")