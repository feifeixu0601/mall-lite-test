from common.random_data import RandomData

print(f"手机号：{RandomData.phone()}")          # 13812345678
print(f"邮箱：{RandomData.email()}")            # test_a8f3@example.com
print(f"用户名：{RandomData.username()}")       # user_kx9m2
print(f"密码：{RandomData.password()}")         # aB3dEfGh2i
print(f"中文名：{RandomData.chinese_name()}")   # 张伟
print(f"地址：{RandomData.address()}")          # 北京市朝阳区中关村大街123号
print(f"随机数：{RandomData.integer(1, 100)}")  # 42
print(f"日期：{RandomData.date_string()}")      # 2024-06-15
print(f"订单号：{RandomData.order_no()}")       # ORD20260807-A3F8K2
print(f"评论：{RandomData.text(5, 10)}")        # 质量不错物流很快推荐购买