"""ProductApi - 商品相关接口（只读，没有增删改）"""

from api_objects.base_api import ApiClient
from common.logger import get_logger

logger = get_logger("product_api")


class ProductApi(ApiClient):

    def get_products(self, keyword=None, category_id=None, page=1, page_size=10):
        """
        获取商品列表

        参数：
            keyword: 搜索关键词（可选）
            category_id: 分类 ID（可选）
            page: 页码
            page_size: 每页数量
        """
        params = {"page": page, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        if category_id:
            params["category_id"] = category_id
        return self.get("/api/products", params=params)

    def get_product(self, product_id):
        """获取商品详情"""
        return self.get(f"/api/products/{product_id}")

    def get_categories(self):
        """获取所有分类"""
        return self.get("/api/categories")