"""
接口签名示例

这个文件不在 MallLite 上运行，是独立的教学示例。
演示如何在测试中生成正确的签名。

运行方式：python api/examples/sign_demo.py
"""

import hashlib
import json


def generate_sign(params, secret_key):
    """
    生成签名

    签名算法：
      1. 把参数按 key 字母排序
      2. 拼接成 key=value&key=value 的格式
      3. 末尾加上 &secret_key=xxx
      4. 对整个字符串做 MD5
    """
    # 按 key 排序
    sorted_keys = sorted(params.keys())

    # 拼接
    sign_str = "&".join(f"{k}={params[k]}" for k in sorted_keys)
    sign_str += f"&secret_key={secret_key}"

    # MD5
    sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
    return sign


# 演示
if __name__ == "__main__":
    # 假设的请求参数
    params = {
        "order_id": "ORD001",
        "amount": "100",
        "user_id": "1",
    }
    secret_key = "my_secret_key"

    sign = generate_sign(params, secret_key)
    print(f"参数：{json.dumps(params, indent=2)}")
    print(f"密钥：{secret_key}")
    print(f"签名：{sign}")

    # 验证：篡改参数后签名不同
    tampered_params = params.copy()
    tampered_params["amount"] = "99999"  # 篡改金额
    tampered_sign = generate_sign(tampered_params, secret_key)

    print(f"\n篡改后签名：{tampered_sign}")
    print(f"签名不同：{sign != tampered_sign}")  # 应该是 True

    # 在测试中的用法：
    # resp = api.post("/api/orders", json_data={
    #     "order_id": "ORD001",
    #     "amount": "100",
    #     "user_id": "1",
    #     "sign": generate_sign(params, secret_key),
    # })