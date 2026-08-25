"""
关键字注册表
维护 "关键字名 → 函数" 的映射关系
引擎通过注册表查找并执行关键字

注册表结构：
    {
        "navigate": <BaseKeywords.navigate>,
        "login": <LoginKeywords.login>,
        "search": <SearchKeywords.search>,
        ...
    }
"""

from common.logger import get_logger
from keywords.base_keywords import BaseKeywords
from keywords.login_keywords import LoginKeywords
from keywords.search_keywords import SearchKeywords
from keywords.cart_keywords import CartKeywords
from keywords.order_keywords import OrderKeywords

logger = get_logger("keyword_registry")


class KeywordRegistry:
    """
    关键字注册表

    负责：
    1. 注册所有关键字类
    2. 根据关键字名查找对应的函数
    3. 管理关键字实例的生命周期

    用法：
        registry = KeywordRegistry(page)
        func = registry.get_keyword("login")
        func("admin", "admin123")
    """

    def __init__(self, page):
        """
        初始化注册表

        参数：
            page: Playwright 的 page 对象
        """
        self.page = page
        self._keywords = {}
        self._keyword_classes = {}

        # 注册所有关键字类
        self._register_all()

    def _register_all(self):
        """注册所有关键字类"""

        # 关键字类列表
        keyword_classes = [
            ("base", BaseKeywords),
            ("login", LoginKeywords),
            ("search", SearchKeywords),
            ("cart", CartKeywords),
            ("order", OrderKeywords),
        ]

        for prefix, cls in keyword_classes:
            self._register_class(prefix, cls)

    def _register_class(self, prefix, cls):
        """
        注册一个关键字类

        参数：
            prefix: 类前缀（用于日志，不参与关键字查找）
            cls: 关键字类
        """
        instance = cls(self.page)
        self._keyword_classes[prefix] = instance

        # 遍历类的所有公开方法，注册为关键字
        for attr_name in dir(instance):
            # 跳过私有方法和特殊方法
            if attr_name.startswith("_"):
                continue

            attr = getattr(instance, attr_name)
            if callable(attr):
                keyword_name = attr_name
                self._keywords[keyword_name] = attr
                logger.debug(f"注册关键字：{keyword_name} → {cls.__name__}.{attr_name}")

        logger.info(f"注册关键字类：{prefix}（{cls.__name__}，{len([m for m in dir(instance) if not m.startswith('_') and callable(getattr(instance, m))])} 个关键字）")

    def get_keyword(self, name):
        """
        根据关键字名获取对应的函数

        参数：
            name: 关键字名称

        返回：
            可调用的函数

        异常：
            KeyError: 关键字不存在时抛出
        """
        if name not in self._keywords:
            available = sorted(self._keywords.keys())
            raise KeyError(
                f"关键字 '{name}' 不存在。"
                f"可用关键字（{len(available)} 个）：{available}"
            )
        return self._keywords[name]

    def has_keyword(self, name):
        """判断关键字是否存在"""
        return name in self._keywords

    def list_keywords(self):
        """列出所有已注册的关键字"""
        return sorted(self._keywords.keys())

    def get_keyword_count(self):
        """获取已注册关键字数量"""
        return len(self._keywords)