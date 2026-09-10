"""
Mock 外部接口示例

这个文件不在 MallLite 上运行，是独立的教学示例。
演示如何用 responses 库 mock 第三方接口。

运行方式：python api/examples/mock_demo.py
"""

import requests
import responses


# ===== 场景：假设订单接口需要调用第三方支付 =====

def create_order_with_payment(order_data):
    """
    创建订单并调用第三方支付接口

    这个函数模拟的是：订单服务先调用支付接口验证支付状态，
    如果支付成功才创建订单。
    """
    # 第一步：调用支付接口
    payment_resp = requests.post(
        "https://pay.example.com/api/verify",
        json={"order_id": order_data["order_id"], "amount": order_data["amount"]},
    )
    payment_result = payment_resp.json()

    if payment_result["status"] == "success":
        return {"code": 200, "message": "订单创建成功", "order_no": "ORD001"}
    else:
        return {"code": 400, "message": "支付失败"}


# ===== 没有 Mock 的情况 =====
# 调用会真的去请求 https://pay.example.com，但这个地址不存在，会报错


# ===== 用 Mock 的情况 =====
@responses.activate
def test_create_order_with_mock_payment():
    """
    用 responses.mock 拦截支付请求，返回预设结果

    知识点：@responses.activate 装饰器
      这个装饰器让 responses 开始拦截 HTTP 请求。
      在函数内注册的 mock 规则，会在函数结束时自动清除。
    """
    # 注册 mock 规则：如果有人 POST https://pay.example.com/api/verify
    # 就返回 {"status": "success"}，状态码 200
    responses.add(
        responses.POST,
        "https://pay.example.com/api/verify",
        json={"status": "success"},
        status=200,
    )

    # 调用被测函数
    result = create_order_with_payment({"order_id": "ORD001", "amount": 8999})

    # 验证结果
    assert result["code"] == 200
    assert result["message"] == "订单创建成功"
    print("✓ Mock 支付成功场景通过")


@responses.activate
def test_create_order_with_failed_payment():
    """模拟支付失败的场景"""
    responses.add(
        responses.POST,
        "https://pay.example.com/api/verify",
        json={"status": "failed", "reason": "余额不足"},
        status=200,
    )

    result = create_order_with_payment({"order_id": "ORD002", "amount": 99999})

    assert result["code"] == 400
    assert result["message"] == "支付失败"
    print("✓ Mock 支付失败场景通过")


if __name__ == "__main__":
    test_create_order_with_mock_payment()
    test_create_order_with_failed_payment()
    print("\n所有 Mock 示例通过")