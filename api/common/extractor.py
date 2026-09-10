"""
响应数据提取器

从 JSON 响应中按路径提取数据，用于接口关联场景

用法：
    body = resp.json()
    name = Extractor.get(body, "data.username")          # "admin"
    first = Extractor.get(body, "data.items.0.name")     # "iPhone 15 Pro"
    names = Extractor.get_all(body, "data.items.*.name") # ["iPhone", "MacBook", ...]
    n = Extractor.count(body, "data.items")               # 15
"""

from common.logger import get_logger

logger = get_logger("extractor")


class Extractor:

    @staticmethod
    def get(data, path, default=None):
        """
        按路径提取值

        路径语法：
            data.username       → 取 data 下的 username
            data.items.0.name   → 取 items 列表第 1 个元素的 name
            data.items.-1.name  → 取最后一个元素的 name
        """
        try:
            parts = path.split(".")
            current = data
            for part in parts:
                if current is None:
                    return default
                if isinstance(current, list):
                    current = current[int(part)]
                elif isinstance(current, dict):
                    current = current[part]
                else:
                    return default
            return current
        except (KeyError, IndexError, TypeError, ValueError):
            return default

    @staticmethod
    def get_all(data, path):
        """
        提取列表中每个元素的某个字段

        路径中 * 表示遍历列表

        用法：
            Extractor.get_all(body, "data.items.*.name")
            返回 ["iPhone 15 Pro", "MacBook Pro", ...]
        """
        parts = path.split(".")
        star_idx = parts.index("*")

        # 定位到列表
        list_path = ".".join(parts[:star_idx])
        items = Extractor.get(data, list_path) if list_path else data

        if not isinstance(items, list):
            return []

        # 从每个元素提取
        remaining = ".".join(parts[star_idx + 1:])
        if not remaining:
            return items

        return [Extractor.get(item, remaining) for item in items
                if Extractor.get(item, remaining) is not None]

    @staticmethod
    def count(data, path):
        """获取列表长度"""
        items = Extractor.get(data, path)
        return len(items) if isinstance(items, list) else 0

    @staticmethod
    def first(data, list_path):
        """获取列表第一个元素"""
        items = Extractor.get(data, list_path)
        return items[0] if isinstance(items, list) and items else None