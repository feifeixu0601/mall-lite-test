"""
MallLite 电商系统 - 商品数据生成脚本
功能：生成商品、分类、用户的基础数据，保存为 JSON 文件
"""

import json
import os

# ========================================
# 第一步：创建数据目录
# ========================================
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"创建数据目录：{data_dir}")
else:
    print(f"数据目录已存在：{data_dir}")

# ========================================
# 第二步：定义商品分类数据
# ========================================
categories = [
    {"id": 1, "name": "手机", "icon": "phone"},
    {"id": 2, "name": "笔记本", "icon": "laptop"},
    {"id": 3, "name": "平板", "icon": "tablet"},
    {"id": 4, "name": "配件", "icon": "accessory"},
]

print(f"\n商品分类：{len(categories)} 个")
for cat in categories:
    print(f"  - {cat['name']}（{cat['icon']}）")

# ========================================
# 第三步：定义商品数据
# ========================================
products = [
    # 手机类
    {
        "id": 1,
        "name": "iPhone 15 Pro",
        "price": 8999,
        "category": "手机",
        "stock": 100,
        "description": "A17 Pro 芯片，钛金属设计，48MP 主摄",
        "is_new": True,
        "rating": 4.8
    },
    {
        "id": 2,
        "name": "iPhone 15",
        "price": 5999,
        "category": "手机",
        "stock": 200,
        "description": "A16 芯片，灵动岛设计，USB-C 接口",
        "is_new": True,
        "rating": 4.7
    },
    {
        "id": 3,
        "name": "华为 Mate 60 Pro",
        "price": 6999,
        "category": "手机",
        "stock": 80,
        "description": "麒麟 9000S，卫星通信，XMAGE 影像",
        "is_new": True,
        "rating": 4.9
    },
    {
        "id": 4,
        "name": "小米 14 Pro",
        "price": 4999,
        "category": "手机",
        "stock": 150,
        "description": "骁龙 8 Gen3，徕卡光学，2K 屏幕",
        "is_new": False,
        "rating": 4.6
    },
    # 笔记本类
    {
        "id": 5,
        "name": "MacBook Pro 14",
        "price": 14999,
        "category": "笔记本",
        "stock": 50,
        "description": "M3 Pro 芯片，18 小时续航，Liquid Retina XDR",
        "is_new": True,
        "rating": 4.9
    },
    {
        "id": 6,
        "name": "ThinkPad X1 Carbon",
        "price": 9999,
        "category": "笔记本",
        "stock": 60,
        "description": "14 英寸，1.12kg，商务旗舰",
        "is_new": False,
        "rating": 4.5
    },
    {
        "id": 7,
        "name": "华为 MateBook X Pro",
        "price": 8999,
        "category": "笔记本",
        "stock": 45,
        "description": "3.1K OLED 触控屏，超窄边框",
        "is_new": False,
        "rating": 4.6
    },
    # 平板类
    {
        "id": 8,
        "name": "iPad Pro 12.9",
        "price": 8999,
        "category": "平板",
        "stock": 70,
        "description": "M2 芯片，Liquid Retina XDR，ProMotion",
        "is_new": False,
        "rating": 4.8
    },
    {
        "id": 9,
        "name": "iPad Air",
        "price": 4799,
        "category": "平板",
        "stock": 120,
        "description": "M1 芯片，10.9 英寸，Touch ID",
        "is_new": False,
        "rating": 4.7
    },
    {
        "id": 10,
        "name": "华为 MatePad Pro",
        "price": 3999,
        "category": "平板",
        "stock": 90,
        "description": "11 英寸 OLED，骁龙 888",
        "is_new": True,
        "rating": 4.5
    },
    # 配件类
    {
        "id": 11,
        "name": "AirPods Pro 2",
        "price": 1899,
        "category": "配件",
        "stock": 300,
        "description": "自适应降噪，个性化空间音频",
        "is_new": False,
        "rating": 4.8
    },
    {
        "id": 12,
        "name": "Apple Watch Series 9",
        "price": 3299,
        "category": "配件",
        "stock": 100,
        "description": "S9 芯片，双指互点手势，亮度翻倍",
        "is_new": True,
        "rating": 4.6
    },
    {
        "id": 13,
        "name": "MagSafe 充电器",
        "price": 399,
        "category": "配件",
        "stock": 500,
        "description": "磁吸对齐，无线充电最高 15W",
        "is_new": False,
        "rating": 4.3
    },
    {
        "id": 14,
        "name": "USB-C 转接头",
        "price": 199,
        "category": "配件",
        "stock": 800,
        "description": "USB-C 转 HDMI + USB-A + SD 卡槽",
        "is_new": False,
        "rating": 4.2
    },
    {
        "id": 15,
        "name": "笔记本支架",
        "price": 299,
        "category": "配件",
        "stock": 200,
        "description": "铝合金材质，可调节高度，散热设计",
        "is_new": False,
        "rating": 4.4
    },
]

print(f"\n商品数据：{len(products)} 个商品")
for p in products:
    print(f"  {p['id']:>2}. {p['name']:<20} ¥{p['price']:<8} [{p['category']}] 库存:{p['stock']}")

# ========================================
# 第四步：定义用户数据
# ========================================
users = [
    {
        "id": 1,
        "username": "admin",
        "password": "admin123",
        "phone": "13800000001",
        "email": "admin@malllite.com",
        "role": "admin",
        "nickname": "管理员"
    },
    {
        "id": 2,
        "username": "testuser",
        "password": "test123",
        "phone": "13800000002",
        "email": "test@malllite.com",
        "role": "user",
        "nickname": "测试用户"
    },
    {
        "id": 3,
        "username": "vipuser",
        "password": "vip123",
        "phone": "13800000003",
        "email": "vip@malllite.com",
        "role": "vip",
        "nickname": "VIP 用户"
    },
]

print(f"\n用户数据：{len(users)} 个用户")
for u in users:
    print(f"  - {u['username']}（{u['role']}）：{u['nickname']}")

# ========================================
# 第五步：保存到 JSON 文件
# ========================================

def save_json(filename, data):
    """将数据保存为 JSON 文件"""
    filepath = os.path.join(data_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已保存：{filepath}（{len(data)} 条数据）")

save_json("products.json", products)
save_json("categories.json", categories)
save_json("users.json", users)

# ========================================
# 第六步：验证 - 读回来试试
# ========================================
print("\n" + "=" * 50)
print("验证：从文件读取数据")
print("=" * 50)

with open(os.path.join(data_dir, "products.json"), "r", encoding="utf-8") as f:
    loaded_products = json.load(f)

print(f"\n从 products.json 读取了 {len(loaded_products)} 个商品")

# 打印第一个商品的信息
first = loaded_products[0]
print(f"\n第一个商品：")
print(f"  名称：{first['name']}")
print(f"  价格：¥{first['price']}")
print(f"  分类：{first['category']}")
print(f"  库存：{first['stock']}")
print(f"  评分：{first['rating']}")

# 统计每个分类的商品数量
print(f"\n各分类商品数量：")
category_count = {}
for p in loaded_products:
    cat = p["category"]
    if cat in category_count:
        category_count[cat] = category_count[cat] + 1
    else:
        category_count[cat] = 1

for cat_name, count in category_count.items():
    print(f"  {cat_name}：{count} 个")

# 统计价格区间
print(f"\n价格统计：")
prices = [p["price"] for p in loaded_products]
print(f"  最低价：¥{min(prices)}")
print(f"  最高价：¥{max(prices)}")
print(f"  平均价：¥{sum(prices) / len(prices):.0f}")

print(f"\n{'=' * 50}")
print("数据生成完成！")
print(f"{'=' * 50}")
