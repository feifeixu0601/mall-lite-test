"""
MallLite 接口响应 Schema 定义

用途：自动校验响应数据的结构和类型是否正确

用法：
    from common.schemas import validate_schema
    validate_schema(resp.json(), "login")         # 校验登录响应
    validate_schema(resp.json(), "product_list")  # 校验商品列表
"""

from common.logger import get_logger

logger = get_logger("schemas")


# MallLite 的接口 Schema 定义
# 每个 Schema 对应一个接口的响应格式

SCHEMAS = {}

# ===== 登录响应 =====
# 探针确认返回：
#   code: 200, message: "登录成功",
#   data: {id: 1, username: "admin", phone: "...", email: "...", role: "admin"}
SCHEMAS["login"] = {
    "type": "object",
    "required": ["code", "message", "data"],
    "properties": {
        "code": {"type": "integer"},
        "message": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["username", "role"],
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "role": {"type": "string"},
                "phone": {"type": ["string", "null"]},
                "email": {"type": ["string", "null"]},
            }
        }
    }
}

# ===== 商品列表 =====
SCHEMAS["product_list"] = {
    "type": "object",
    "required": ["code", "data"],
    "properties": {
        "code": {"type": "integer"},
        "data": {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "price"],
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "price": {"type": "number"},
                        }
                    }
                }
            }
        }
    }
}

# ===== 商品详情 =====
SCHEMAS["product_detail"] = {
    "type": "object",
    "required": ["code", "data"],
    "properties": {
        "code": {"type": "integer"},
        "data": {
            "type": "object",
            "required": ["name", "price"],
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "stock": {"type": "integer"},
                "description": {"type": ["string", "null"]},
            }
        }
    }
}

# ===== 购物车 =====
SCHEMAS["cart"] = {
    "type": "object",
    "required": ["code", "data"],
    "properties": {
        "code": {"type": "integer"},
        "data": {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["product_id", "quantity"],
                        "properties": {
                            "product_id": {"type": "integer"},
                            "quantity": {"type": "integer"},
                        }
                    }
                },
                "total_price": {"type": "number"},
                "total_quantity": {"type": "integer"},
                "item_count": {"type": "integer"},
            }
        }
    }
}

# ===== 订单 =====
SCHEMAS["order_detail"] = {
    "type": "object",
    "required": ["code", "data"],
    "properties": {
        "code": {"type": "integer"},
        "data": {
            "type": "object",
            "required": ["order_no", "status", "items"],
            "properties": {
                "order_no": {"type": "string"},
                "status": {"type": "string"},
                "items": {"type": "array"},
                "total_price": {"type": "number"},
            }
        }
    }
}

# ===== 分类列表 =====
SCHEMAS["category_list"] = {
    "type": "object",
    "required": ["code", "data"],
    "properties": {
        "code": {"type": "integer"},
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name"],
            }
        }
    }
}


def validate_schema(data, schema_name):
    """
    校验数据是否符合 Schema

    参数：
        data: 要校验的数据（通常是 resp.json()）
        schema_name: Schema 名称

    用法：
        validate_schema(resp.json(), "login")
        validate_schema(resp.json(), "product_list")

    通过：无返回
    失败：抛出 jsonschema.ValidationError
    """
    from jsonschema import validate

    schema = SCHEMAS.get(schema_name)
    if schema is None:
        raise ValueError(f"Schema '{schema_name}' 不存在。可用：{list(SCHEMAS.keys())}")

    validate(instance=data, schema=schema)
    logger.debug(f"Schema 校验通过：{schema_name}")

def auto_validate(schema_name):
    """
    自动 Schema 校验装饰器

    用法：
        @auto_validate("login")
        def test_login(self, user_api):
            resp = user_api.login("admin", "admin123")
            return resp  # 装饰器会自动校验响应的 Schema

    知识点：装饰器是什么？
        装饰器是一个函数，它"包裹"另一个函数，在原函数执行前后做额外的事情。
        这里的 auto_validate 在测试函数执行后，自动对返回的 response 做 Schema 校验。
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # 如果函数返回了一个 requests.Response 对象，自动校验
            import requests
            if isinstance(result, requests.Response):
                validate_schema(result.json(), schema_name)
            return result

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator

def generate_schema(data, max_depth=3):
    """
    从实际响应数据自动生成 JSON Schema 骨架

    参数：
        data: 实际的 JSON 数据（通常是 resp.json()）
        max_depth: 最大递归深度（避免无限嵌套）

    返回：
        JSON Schema 字典

    用法：
        resp = user_api.login("admin", "admin123")
        schema = generate_schema(resp.json())
        print(json.dumps(schema, indent=2, ensure_ascii=False))
        # 输出可以作为 SCHEMAS 字典中的定义

    知识点：为什么要自动生成？
        手写 Schema 需要逐个字段写 type、required。
        如果接口有 50 个字段，手写容易漏。
        自动生成一个骨架，再人工微调，效率高很多。
    """
    if max_depth <= 0:
        return {}

    if isinstance(data, dict):
        schema = {"type": "object", "required": list(data.keys()), "properties": {}}
        for key, value in data.items():
            schema["properties"][key] = generate_schema(value, max_depth - 1)
        return schema

    elif isinstance(data, list):
        schema = {"type": "array"}
        if data:
            schema["items"] = generate_schema(data[0], max_depth - 1)
        return schema

    elif isinstance(data, bool):
        return {"type": "boolean"}

    elif isinstance(data, int):
        return {"type": "integer"}

    elif isinstance(data, float):
        return {"type": "number"}

    elif isinstance(data, str):
        return {"type": "string"}

    elif data is None:
        return {"type": "null"}

    return {}