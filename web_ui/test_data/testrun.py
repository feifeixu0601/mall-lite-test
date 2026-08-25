from common.data_reader import DataReader

# 读取 JSON
login_data = DataReader.read_json("login_data.json")
for case in login_data:
    print(f"  {case['case_name']}：{case['username']} / {case['password']}")

# 读取 YAML
search_data = DataReader.read_yaml("search_data.yaml")
for case in search_data["search_cases"]:
    print(f"  {case['case_name']}：搜索 '{case['keyword']}'")

# 读取 CSV
cart_data = DataReader.read_csv("cart_data.csv")
for row in cart_data:
    print(f"  {row['case_name']}：商品 {row['product_name']} × {row['quantity']}")