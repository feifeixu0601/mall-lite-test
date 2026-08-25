"""
MallLite 自动化测试 - 随机数据生成器
生成测试用的随机手机号、邮箱、用户名等

用法：
    from common.random_data import RandomData

    phone = RandomData.phone()           # "13812345678"
    email = RandomData.email()           # "test_a8f3@example.com"
    username = RandomData.username()     # "user_kx9m2"
    name = RandomData.chinese_name()     # "张三"
    address = RandomData.address()       # "北京市朝阳区xxx路xxx号"
"""

import random
import string
import time
from datetime import datetime, timedelta


class RandomData:
    """随机数据生成器"""

    # 常量
    SURNAMES = ["张", "李", "王", "赵", "刘", "陈", "杨", "黄", "周", "吴",
                "徐", "孙", "马", "胡", "朱", "郭", "何", "罗", "高", "林"]
    NAMES = ["伟", "芳", "娜", "敏", "静", "强", "磊", "洋", "勇", "艳",
             "杰", "丽", "军", "超", "明", "霞", "秀英", "华", "平", "刚"]
    CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "重庆"]
    DISTRICTS = ["朝阳区", "海淀区", "浦东新区", "天河区", "南山区", "西湖区", "锦江区", "江汉区"]
    STREETS = ["中关村大街", "南京路", "天府大道", "深南大道", "西湖大道", "解放路", "建设路", "人民路"]

    @staticmethod
    def _random_chars(length=5, chars=string.ascii_lowercase + string.digits):
        """生成随机字符"""
        return "".join(random.choices(chars, k=length))

    @staticmethod
    def phone():
        """
        生成随机手机号

        返回：
            11 位手机号字符串，如 "13812345678"
        """
        prefixes = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
                     "150", "151", "152", "153", "155", "156", "157", "158", "159",
                     "170", "176", "177", "178",
                     "180", "181", "182", "183", "184", "185", "186", "187", "188", "189"]
        prefix = random.choice(prefixes)
        suffix = "".join([str(random.randint(0, 9)) for _ in range(8)])
        return prefix + suffix

    @staticmethod
    def email(domain="example.com"):
        """
        生成随机邮箱

        参数：
            domain: 邮箱域名

        返回：
            邮箱字符串，如 "test_a8f3@example.com"
        """
        prefix = f"test_{RandomData._random_chars(6)}"
        return f"{prefix}@{domain}"

    @staticmethod
    def username(prefix="user", length=5):
        """
        生成随机用户名

        参数：
            prefix: 前缀
            length: 随机部分长度

        返回：
            用户名字符串，如 "user_kx9m2"
        """
        return f"{prefix}_{RandomData._random_chars(length)}"

    @staticmethod
    def password(length=10):
        """
        生成随机密码（包含字母和数字）

        参数：
            length: 密码长度

        返回：
            密码字符串
        """
        # 确保至少有一个字母和一个数字
        letters = random.choices(string.ascii_letters, k=length - 2)
        digits = random.choices(string.digits, k=2)
        password_list = letters + digits
        random.shuffle(password_list)
        return "".join(password_list)

    @staticmethod
    def chinese_name():
        """
        生成随机中文姓名

        返回：
            中文姓名，如 "张伟"
        """
        surname = random.choice(RandomData.SURNAMES)
        name = random.choice(RandomData.NAMES)
        return surname + name

    @staticmethod
    def address():
        """
        生成随机地址

        返回：
            地址字符串，如 "北京市朝阳区中关村大街123号"
        """
        city = random.choice(RandomData.CITIES)
        district = random.choice(RandomData.DISTRICTS)
        street = random.choice(RandomData.STREETS)
        number = random.randint(1, 999)
        return f"{city}{district}{street}{number}号"

    @staticmethod
    def integer(min_val=1, max_val=9999):
        """生成随机整数"""
        return random.randint(min_val, max_val)

    @staticmethod
    def float_number(min_val=0.01, max_val=9999.99, decimal_places=2):
        """生成随机浮点数"""
        return round(random.uniform(min_val, max_val), decimal_places)

    @staticmethod
    def date(start_year=2020, end_year=2026):
        """
        生成随机日期

        返回：
            datetime 对象
        """
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        delta = end - start
        random_days = random.randint(0, delta.days)
        return start + timedelta(days=random_days)

    @staticmethod
    def date_string(start_year=2020, end_year=2026, fmt="%Y-%m-%d"):
        """
        生成随机日期字符串

        返回：
            日期字符串，如 "2024-06-15"
        """
        return RandomData.date(start_year, end_year).strftime(fmt)

    @staticmethod
    def order_no():
        """
        生成随机订单号

        返回：
            订单号字符串，如 "ORD20260807-A3F8K2"
        """
        date_str = datetime.now().strftime("%Y%m%d")
        suffix = RandomData._random_chars(6, string.ascii_uppercase + string.digits)
        return f"ORD{date_str}-{suffix}"

    @staticmethod
    def text(min_words=5, max_words=20):
        """
        生成随机中文文本（模拟评论、描述等）

        参数：
            min_words: 最少字数
            max_words: 最多字数

        返回：
            随机文本字符串
        """
        words = ["这个", "商品", "非常", "好用", "质量", "不错", "物流", "很快",
                 "包装", "精美", "性价比", "很高", "推荐", "购买", "下次", "还会",
                 "回购", "满意", "惊喜", "超出预期", "手感", "很好", "外观", "漂亮",
                 "价格", "实惠", "做工", "精细", "发货", "速度快", "服务", "态度好"]
        length = random.randint(min_words, max_words)
        return "".join(random.choices(words, k=length))

    @staticmethod
    def unique_id():
        """
        生成唯一 ID（基于时间戳 + 随机数）

        返回：
            唯一 ID 字符串
        """
        timestamp = int(time.time() * 1000)
        suffix = random.randint(1000, 9999)
        return f"{timestamp}{suffix}"