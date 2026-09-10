import os

# 确保目录存在
os.makedirs("../test_data", exist_ok=True)

from openpyxl import Workbook

wb = Workbook()

# Sheet 1：登录成功
ws1 = wb.active
ws1.title = "登录成功"
ws1.append(["case_name", "username", "password", "expected_role"])
ws1.append(["管理员", "admin", "admin123", "admin"])
ws1.append(["普通用户", "testuser", "test123", "user"])
ws1.append(["VIP用户", "vipuser", "vip123", "vip"])

# Sheet 2：登录失败
ws2 = wb.create_sheet("登录失败")
ws2.append(["case_name", "username", "password", "expected_msg"])
ws2.append(["密码错误", "admin", "wrong", "密码错误"])
ws2.append(["用户不存在", "nobody", "123", "用户不存在"])
ws2.append(["用户名为空", "", "admin123", "请输入用户名"])
ws2.append(["密码为空", "admin", "", "请输入密码"])

wb.save("../test_data/login_cases.xlsx")
print("Excel 文件已生成：test_data/login_cases.xlsx")