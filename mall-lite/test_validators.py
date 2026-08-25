"""测试表单验证器"""

from app.validators import Validator

print("【表单验证测试】")
print("=" * 60)

# ====== 手机号验证 ======
print("\n手机号验证：")
phone_tests = [
    ("13800138000", True),
    ("15912345678", True),
    ("12345678901", False),   # 12 开头不合法
    ("1380013800", False),    # 只有 10 位
    ("138001380001", False),  # 12 位
    ("abcdefghijk", False),   # 非数字
    ("", False),              # 空
]

for phone, expected in phone_tests:
    result = Validator.is_valid_phone(phone)
    status = "✅" if result == expected else "❌"
    print(f"  {status} {phone or '(空)':<15} → {result}")

# ====== 邮箱验证 ======
print("\n邮箱验证：")
email_tests = [
    ("test@example.com", True),
    ("user.name@corp.cn", True),
    ("admin@163.com", True),
    ("invalid", False),
    ("@example.com", False),
    ("test@", False),
    ("", False),
]

for email, expected in email_tests:
    result = Validator.is_valid_email(email)
    status = "✅" if result == expected else "❌"
    print(f"  {status} {email or '(空)':<25} → {result}")

# ====== 用户名验证 ======
print("\n用户名验证：")
username_tests = [
    ("admin", True),
    ("test_user123", True),
    ("ab", False),          # 太短
    ("123user", False),     # 数字开头
    ("a" * 21, False),      # 太长
    ("", False),
]

for username, expected in username_tests:
    result = Validator.is_valid_username(username)
    status = "✅" if result == expected else "❌"
    print(f"  {status} {username or '(空)':<20} → {result}")

# ====== 密码验证 ======
print("\n密码验证：")
password_tests = [
    ("admin123", True),
    ("pass1word", True),
    ("abc", False),          # 太短
    ("abcdefgh", False),     # 没有数字
    ("12345678", False),     # 没有字母
    ("", False),
]

for password, expected in password_tests:
    result = Validator.is_valid_password(password)
    status = "✅" if result == expected else "❌"
    display = password if password else "(空)"
    print(f"  {status} {display:<20} → {result}")

# ====== 注册表单完整验证 ======
print("\n注册表单完整验证：")

register_tests = [
    {
        "name": "正常注册",
        "data": {"username": "newuser", "password": "pass123", "phone": "13800138000", "email": "test@test.com"},
        "expected_valid": True,
    },
    {
        "name": "用户名不合法",
        "data": {"username": "123bad", "password": "pass123"},
        "expected_valid": False,
    },
    {
        "name": "密码太简单",
        "data": {"username": "newuser", "password": "123"},
        "expected_valid": False,
    },
    {
        "name": "手机号格式错",
        "data": {"username": "newuser", "password": "pass123", "phone": "123"},
        "expected_valid": False,
    },
    {
        "name": "多个字段错误",
        "data": {"username": "12", "password": "abc", "phone": "123", "email": "bad"},
        "expected_valid": False,
    },
]

for test in register_tests:
    is_valid, errors = Validator.validate_register_form(test["data"])
    status = "✅" if is_valid == test["expected_valid"] else "❌"
    print(f"\n  {status} {test['name']}：{'通过' if is_valid else '失败'}")
    if errors:
        for err in errors:
            print(f"      - {err}")

# ====== 正则提取测试 ======
print("\n\n【正则提取测试】")
print("=" * 60)

import re

# 从接口响应中提取订单号
response = '{"code":200,"message":"订单 ORD20260807-000042 创建成功","data":{"order_no":"ORD20260807-000042"}}'

order_match = re.search(r"(ORD\d{8}-\d{6})", response)
if order_match:
    print(f"  提取订单号：{order_match.group(1)}")

# 从错误消息中提取信息
error_msg = "库存不足：需要 5 件，剩余 2 件"
stock_match = re.search(r"需要 (\d+) 件，剩余 (\d+) 件", error_msg)
if stock_match:
    print(f"  需要：{stock_match.group(1)}，剩余：{stock_match.group(2)}")

# 从 URL 中提取参数
url = "http://localhost:8000/api/products?page=2&page_size=10&category=手机"
params = re.findall(r"(\w+)=([^&]+)", url.split("?")[1] if "?" in url else "")
print(f"  URL 参数：{dict(params)}")

# 日志脱敏
log = "用户 13800138000 登录，邮箱 admin@malllite.com"
masked = re.sub(r"(1\d{2})\d{4}(\d{4})", r"\1****\2", log)
masked = re.sub(r"(\w{2})\w+(@[\w.]+)", r"\1***\2", masked)
print(f"  脱敏前：{log}")
print(f"  脱敏后：{masked}")

# 测试结果统计
print("\n\n【Counter 统计测试结果】")
print("=" * 60)

from collections import Counter

test_results = [
    "PASSED", "PASSED", "FAILED", "PASSED", "PASSED",
    "SKIPPED", "PASSED", "FAILED", "PASSED", "PASSED",
    "PASSED", "ERROR", "PASSED", "PASSED", "SKIPPED",
]

counter = Counter(test_results)
total = sum(counter.values())

print(f"  总用例数：{total}")
print(f"  通过：{counter['PASSED']}（{counter['PASSED']/total*100:.1f}%）")
print(f"  失败：{counter['FAILED']}（{counter['FAILED']/total*100:.1f}%）")
print(f"  跳过：{counter['SKIPPED']}（{counter['SKIPPED']/total*100:.1f}%）")
print(f"  异常：{counter['ERROR']}（{counter['ERROR']/total*100:.1f}%）")
print(f"  通过率：{counter['PASSED']/total*100:.1f}%")