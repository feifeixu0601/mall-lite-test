"""
CartApi - 购物车相关接口（完善版）

关键点（来自探针脚本验证）：
  - 购物车的增删改查都用 product_id，不是 cart_item_id
  - 未登录访问购物车：code=200 + 返回空数据
  - 未登录添加购物车：code=200 + 添加成功（MallLite 的实际行为）

接口：
  GET    /api/cart            获取购物车
  POST   /api/cart            添加商品     body: {"product_id":1, "quantity":2}
  PUT    /api/cart/{product_id}  修改数量  body: {"quantity":5}
  DELETE /api/cart/{product_id}  删除商品
"""

from api_objects.base_api import ApiClient
from common.logger import get_logger

logger = get_logger("cart_api")


class CartApi(ApiClient):

    def get_cart(self):
        """获取购物车列表"""
        return self.get("/api/cart")

    def add_to_cart(self, product_id, quantity=1):
        """
        添加商品到购物车

        参数：
            product_id: 商品 ID
            quantity: 数量（默认 1）
        """
        logger.info(f"添加到购物车：商品ID={product_id}，数量={quantity}")
        return self.post("/api/cart", json_data={
            "product_id": product_id,
            "quantity": quantity,
        })

    def update_quantity(self, product_id, quantity):
        """
        修改购物车中某商品的数量

        参数：
            product_id: 商品 ID（不是购物车记录 ID）
            quantity: 新数量
        """
        logger.info(f"修改数量：商品ID={product_id} → {quantity}")
        return self.put(f"/api/cart/{product_id}", json_data={
            "quantity": quantity,
        })

    def delete_from_cart(self, product_id):
        """
        从购物车删除某商品

        参数：
            product_id: 商品 ID
        """
        logger.info(f"删除购物车商品：商品ID={product_id}")
        return self.delete(f"/api/cart/{product_id}")

    def clear_cart(self):
        """
        清空购物车（便捷方法）

        获取所有商品，逐个删除
        """
        resp = self.get_cart()
        data = resp.json()
        if data.get("code") == 200:
            items = data["data"]["items"]
            for item in items:
                self.delete_from_cart(item["product_id"])
            logger.info(f"购物车已清空（删除 {len(items)} 个商品）")