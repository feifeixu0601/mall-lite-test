# MallLite 电商系统 & 自动化测试（API + Web UI）

本项目包含三大部分：

1. **mall-lite**：基于 FastAPI 的轻量级电商系统（被测系统）
2. **api**：基于 Pytest + Requests 的 API 自动化测试框架，支持数据驱动、Schema 校验、链路测试
3. **web_ui**：基于 Pytest + Playwright 的 Web UI 自动化测试框架，支持 POM / KDT / BDD 三种测试模式

---

## 目录结构

```
autotestskill/
├── mall-lite/                 # 电商系统（被测对象）
│   ├── app/
│   │   ├── routers/           # 路由层（页面路由 + API 路由）
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── models.py          # 数据模型
│   │   ├── data_store.py      # JSON 数据存储层
│   │   ├── validators.py      # 数据校验
│   │   └── logger.py          # 日志模块
│   ├── data/                  # JSON 数据文件（用户、商品、订单等）
│   ├── backup/                # 数据备份目录
│   ├── templates/             # Jinja2 HTML 模板
│   ├── static/css/            # 静态样式文件
│   ├── requirements.txt       # 电商系统依赖
│   └── run.py                 # 电商系统启动脚本
│
├── api/                       # API 自动化测试框架
│   ├── api_objects/           # API 对象层（类似 POM）
│   │   ├── base_api.py        # ApiClient 基类（重试/超时/日志）
│   │   ├── user_api.py        # 用户接口（登录/注册）
│   │   ├── product_api.py     # 商品接口（列表/详情/分类）
│   │   ├── cart_api.py        # 购物车接口（增删改查）
│   │   └── order_api.py       # 订单接口（创建/列表/详情）
│   ├── common/                # 公共工具模块
│   │   ├── assertions.py      # 链式断言工具（ApiAssertions）
│   │   ├── extractor.py       # 响应数据提取器（路径语法）
│   │   ├── schemas.py         # JSON Schema 定义与校验
│   │   ├── logger.py          # 日志封装
│   │   ├── data_reader.py     # 测试数据读取（YAML/Excel）
│   │   └── response_validator.py  # 响应校验器
│   ├── test_cases/            # 测试用例
│   │   ├── test_user.py       # 用户模块
│   │   ├── test_product.py    # 商品模块
│   │   ├── test_cart.py       # 购物车模块
│   │   ├── test_order.py      # 订单模块
│   │   ├── test_shopping_flow.py  # 端到端链路测试
│   │   ├── test_auth.py       # 鉴权验证专题
│   │   ├── test_data_consistency.py  # 跨接口数据一致性
│   │   ├── test_edge_cases.py # 边界值 & 异常场景
│   │   ├── test_resilience.py # 容错/重试/并发测试
│   │   ├── test_pagination.py # 分页验证
│   │   ├── test_session.py    # Session 管理
│   │   ├── test_schema_auto.py    # Schema 自动校验
│   │   ├── test_yaml_drive.py # YAML 数据驱动
│   │   ├── test_excel_drive.py    # Excel 数据驱动
│   │   ├── test_allure_demo.py    # Allure 报告演示
│   │   └── test_extractor_practice.py  # 数据提取器练习
│   ├── test_data/             # 测试数据文件（YAML/Excel）
│   ├── allure-results/        # Allure 报告数据
│   ├── conftest.py            # Pytest Fixtures（共享登录/自动清理）
│   ├── pytest.ini             # Pytest 配置文件
│   └── requirements.txt       # API 测试依赖
│
└── web_ui/                    # Web UI 自动化测试框架
    ├── common/                # 公共工具模块
    │   ├── logger.py          # 日志封装
    │   ├── screenshot.py      # 截图工具
    │   ├── allure_helper.py   # Allure 报告辅助
    │   ├── data_reader.py     # 测试数据读取（YAML/JSON/CSV）
    │   └── random_data.py     # 随机数据生成
    ├── config/                # 配置管理
    │   ├── config.py          # 多环境配置类
    │   └── env_config.yaml    # 环境配置文件（dev/staging/prod）
    ├── engine/                # 测试引擎
    │   └── test_engine.py     # KDT 关键字驱动引擎
    ├── keywords/              # KDT 关键字库
    │   ├── base_keywords.py   # 基础关键字
    │   ├── login_keywords.py  # 登录关键字
    │   ├── search_keywords.py # 搜索关键字
    │   ├── cart_keywords.py   # 购物车关键字
    │   ├── order_keywords.py  # 订单关键字
    │   └── keyword_registry.py# 关键字注册中心
    ├── pages/                 # POM 页面对象
    │   ├── base_page.py       # 基础页面类
    │   ├── login_page.py      # 登录页
    │   ├── home_page.py       # 首页
    │   ├── product_page.py    # 商品详情页
    │   ├── cart_page.py       # 购物车页
    │   ├── order_page.py      # 订单页
    │   └── profile_page.py    # 个人中心页
    ├── test_cases/            # 测试用例（三种模式）
    │   ├── pom/               # POM 模式用例
    │   ├── kdt/               # KDT 关键字驱动用例（YAML）
    │   └── bdd/               # BDD 行为驱动用例
    │       ├── features/      # .feature 场景文件
    │       └── steps/         # 步骤定义
    ├── test_data/             # 测试数据文件（YAML/JSON/CSV）
    ├── reports/               # 测试报告输出目录
    ├── conftest.py            # Pytest 全局配置 & Fixtures
    ├── pytest.ini             # Pytest 配置文件
    ├── behave.ini             # Behave (BDD) 配置文件
    ├── allure_config.py       # Allure 报告配置生成
    ├── requirements.txt       # 测试框架依赖
    └── run.py                 # 测试一键运行脚本
```

---

## 一、电商系统 (mall-lite)

### 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| FastAPI | 0.109.0 | Web 框架 |
| Uvicorn | 0.27.0 | ASGI 服务器 |
| Jinja2 | 3.1.3 | 模板引擎 |
| python-multipart | 0.0.6 | 表单数据解析 |
| PyYAML | 6.0.1 | YAML 解析 |

### 功能模块

- 🔐 用户登录 / 注册（支持 admin / user / vip 三种角色）
- 🏠 商品首页（分类浏览、商品列表）
- 🔍 商品搜索（按名称、分类搜索）
- 📦 商品详情页
- 🛒 购物车管理（添加、删除、修改数量）
- 📝 订单管理（下单、查看订单列表）
- 👤 个人中心

### 预置测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| testuser | test123 | 普通用户 |
| vipuser | vip123 | VIP 用户 |

### 启动电商系统

```bash
cd mall-lite

# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动系统
python run.py
```

启动成功后访问：

- 系统首页：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## 二、API 自动化测试 (api)

### 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Requests | 2.32.3 | HTTP 请求库 |
| Pytest | 8.3.4 | 测试运行框架 |
| Allure-Pytest | 2.13.5 | Allure 测试报告 |
| jsonschema | 4.23.0 | JSON Schema 校验 |
| PyYAML | 6.0.2 | YAML 解析 |

### 核心架构

API 测试框架采用 **API Object 模式**（类似 Web UI 的 POM），将接口请求封装到独立的 API 类中，用例代码只关注业务逻辑。

#### 1. ApiClient 基类

[base_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/base_api.py) 提供统一的 HTTP 请求能力：

- **自动重试**：GET/PUT/DELETE 对 5xx 错误自动重试 2 次（带退避间隔），POST 不重试避免重复创建
- **可配置超时**：默认 10 秒，单个接口可覆盖
- **Session 管理**：支持上下文管理器（with 语法），确保异常时也能关闭
- **统一日志**：请求/响应自动格式化输出，含耗时统计
- **请求统计**：`_request_count` / `_fail_count` 追踪请求数量和失败率

**示例：**
```python
from api_objects.base_api import ApiClient

with ApiClient("http://localhost:8000") as api:
    resp = api.get("/api/products")
    resp = api.post("/api/login", json_data={"username": "admin", "password": "admin123"})
```

#### 2. API 对象层

| API 类 | 文件 | 主要接口 |
|--------|------|---------|
| UserApi | [user_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/user_api.py) | 登录、注册、获取用户信息 |
| ProductApi | [product_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/product_api.py) | 商品列表、商品详情、分类列表 |
| CartApi | [cart_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/cart_api.py) | 加购、修改数量、删除、清空购物车 |
| OrderApi | [order_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/order_api.py) | 创建订单、订单列表、订单详情 |

**Session 共享机制**：`UserApi.login_and_share()` 登录后返回包含 Cookie 的 Session 对象，可直接赋值给 CartApi / OrderApi 的 `session` 属性，实现跨 API 类共享登录状态。

#### 3. 公共工具模块

| 模块 | 文件 | 功能 |
|------|------|------|
| ApiAssertions | [assertions.py](file:///d:/Faye/project/autotestskill/api/common/assertions.py) | 链式断言：业务码、消息、字段、列表、Schema、响应时间 |
| Extractor | [extractor.py](file:///d:/Faye/project/autotestskill/api/common/extractor.py) | 按路径提取 JSON 数据，支持列表索引和通配符 `*` |
| SCHEMAS + validate_schema | [schemas.py](file:///d:/Faye/project/autotestskill/api/common/schemas.py) | JSON Schema 定义、自动校验、装饰器模式、Schema 自动生成 |
| data_reader | [data_reader.py](file:///d:/Faye/project/autotestskill/api/common/data_reader.py) | 读取 YAML / Excel 测试数据文件 |

**ApiAssertions 链式断言示例：**
```python
from common.assertions import ApiAssertions

resp = user_api.login("admin", "admin123")
ApiAssertions(resp) \
    .assert_success() \
    .assert_has_field("data.username") \
    .assert_field_value("data.role", "admin") \
    .assert_response_time(2.0) \
    .assert_schema("login")
```

**Extractor 路径语法示例：**
```python
body = resp.json()
name = Extractor.get(body, "data.username")           # 取 data.username
first_name = Extractor.get(body, "data.items.0.name") # 取列表第 1 个的 name
names = Extractor.get_all(body, "data.items.*.name")  # 取所有元素的 name 列表
```

### 测试用例分类

API 测试用例覆盖从基础正向到高级专项的完整维度：

| 类别 | 测试文件 | 覆盖内容 |
|------|---------|---------|
| **基础模块** | [test_user.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_user.py) | 登录/注册 正向 + 反向 |
| | [test_product.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_product.py) | 商品列表/详情/分类/搜索/分页 |
| | [test_cart.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_cart.py) | 加购/修改/删除/清空 |
| | [test_order.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_order.py) | 下单/订单列表/详情 |
| **端到端链路** | [test_shopping_flow.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_shopping_flow.py) | 新用户完整流程：注册→登录→搜索→加购→改数量→下单→查单；链式 Fixture 演示 |
| **鉴权专题** | [test_auth.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_auth.py) | 登录返回 Session 信息、密码错误无有效 Session、登录/退出行为、JWT 模拟 |
| **数据一致性** | [test_data_consistency.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_data_consistency.py) | 商品列表vs详情、搜索结果vs详情、订单列表vs详情、金额小计之和=总金额 |
| **边界 & 异常** | [test_edge_cases.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_edge_cases.py) | 购物车数量(0/负数/极大值)、空购物车下单、连续下单两次、恶意输入(SQL注入/XSS) |
| **容错 & 并发** | [test_resilience.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_resilience.py) | 超时验证、重试策略验证、多线程并发加购/登录/下单 |
| **分页** | [test_pagination.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_pagination.py) | 分页参数边界、页码超出、每页大小边界 |
| **Schema 校验** | [test_schema_auto.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_schema_auto.py) | JSON Schema 自动校验、装饰器模式 |
| **数据驱动** | [test_yaml_drive.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_yaml_drive.py) | YAML 文件驱动购物车/订单用例 |
| | [test_excel_drive.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_excel_drive.py) | Excel 驱动登录用例（非技术人员可编辑） |
| **报告 & 工具** | [test_allure_demo.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_allure_demo.py) | Allure 报告功能演示 |
| | [test_extractor_practice.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_extractor_practice.py) | 数据提取器练习用例 |
| | [test_session.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_session.py) | Session 管理专题 |

### 核心 Fixture 设计

在 [conftest.py](file:///d:/Faye/project/autotestskill/api/conftest.py) 中定义：

#### Session 级共享登录（整个测试会话只登录一次）
```python
@pytest.fixture(scope="session")
def admin_session():
    """管理员登录 Session，所有用例共享，节省大量登录时间"""
    user = UserApi(BASE_URL)
    return user.login_and_share("admin", "admin123")
```

#### 已登录的 API 客户端（共享 Session）
| Fixture | 说明 |
|---------|------|
| `admin_user_api` | 已登录的 UserApi |
| `admin_cart_api` | 已登录的 CartApi |
| `admin_order_api` | 已登录的 OrderApi |
| `user_api` / `product_api` / `cart_api` / `order_api` | 未登录版本（用于鉴权测试） |

#### 自动清理（防数据污染）
```python
@pytest.fixture(autouse=True)
def clean_cart(admin_session):
    """每个用例执行前自动清空购物车，避免用例间数据互相影响"""
    cart = CartApi(BASE_URL)
    cart.session = admin_session
    cart.clear_cart()
    yield  # 用例执行
```

#### 链式 Fixture（前置数据准备）
| Fixture | 说明 |
|---------|------|
| `created_order` | 自动加购 → 创建订单，返回 `order_no`，用例直接使用 |
| `first_product` | 自动获取商品列表第一个商品，返回完整信息 `{"id":..., "name":..., "price":...}` |
| `unique_username` | 用时间戳生成唯一用户名，用于注册接口独立数据 |
| `admin_account` | 管理员账号字典 `{"username":"admin","password":"admin123"}` |
| `assert_api` | 返回 ApiAssertions 类 |

### 快速开始

#### 1. 安装依赖

```bash
cd api
pip install -r requirements.txt
```

#### 2. 确保电商系统已启动

请先启动 **mall-lite** 电商系统（默认监听 8000 端口）。

#### 3. 运行测试

```bash
# 基础运行（已在 pytest.ini 中配置 -v --alluredir）
pytest

# 运行冒烟测试（P0 核心链路）
pytest -m "smoke or p0"

# 运行回归测试（全量）
pytest -m regression

# 只跑某个模块
pytest -m login       # 登录模块
pytest -m cart        # 购物车模块
pytest -m order       # 订单模块
pytest -m product     # 商品模块

# 只跑正向 / 反向
pytest -m positive
pytest -m negative

# 指定优先级
pytest -m p0
pytest -m "p0 or p1"

# 运行单个文件
pytest test_cases/test_shopping_flow.py -v

# 运行单个用例
pytest test_cases/test_shopping_flow.py::TestShoppingFlow::test_new_user_full_flow -v
```

#### 4. 查看 Allure 报告

```bash
# 1. 运行测试已自动生成 allure-results 数据
# 2. 启动 Allure 报告服务
allure serve allure-results
```

报告特性：
- 📊 用例通过率 / 按模块 / 按优先级统计
- 📝 详细请求/响应日志
- ❌ 失败自动附加异常堆栈信息
- 🔍 用例详细步骤（docstring 展示）

### 自定义 Pytest Markers

在 [pytest.ini](file:///d:/Faye/project/autotestskill/api/pytest.ini) 中定义：

| Marker | 说明 |
|--------|------|
| `@pytest.mark.smoke` | 冒烟测试（核心功能） |
| `@pytest.mark.regression` | 回归测试（全量） |
| `@pytest.mark.login` / `register` | 用户模块 |
| `@pytest.mark.product` / `category` | 商品模块 |
| `@pytest.mark.cart` | 购物车模块 |
| `@pytest.mark.order` | 订单模块 |
| `@pytest.mark.positive` | 正向用例 |
| `@pytest.mark.negative` | 反向用例（含边界/异常） |
| `@pytest.mark.schema` | Schema 校验用例 |
| `@pytest.mark.p0` / `p1` / `p2` | 优先级（高→中→低） |

---

## 三、Web UI 自动化测试 (web_ui)

### 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Playwright | 1.49.1 | 浏览器自动化驱动 |
| Pytest | 8.3.4 | 测试运行框架 |
| Allure-Pytest | 2.16.0 | Allure 测试报告 |
| Behave | 1.3.3 | BDD 行为驱动框架 |
| PyYAML | 6.0.2 | YAML 解析 |
| openpyxl | 3.1.5 | Excel 数据读取 |
| pytest-xdist | 3.5.0 | 并发执行 |
| pytest-rerunfailures | 14.0 | 失败重试 |
| pytest-ordering | 0.6 | 用例执行顺序 |
| pytest-html | 4.1.1 | HTML 报告 |

### 支持的测试模式

#### 1. POM 模式（Page Object Model）

页面对象模式，将页面元素定位和操作封装到独立的 Page 类中，用例代码简洁易维护。

**示例：** [test_login.py](file:///d:/Faye/project/autotestskill/web_ui/test_cases/pom/test_login.py)

```python
def test_login_success(login_page, home_page, normal_user):
    login_page.goto()
    login_page.login(normal_user["username"], normal_user["password"])
    assert home_page.is_logged_in()
    assert normal_user["nickname"] in home_page.get_welcome_text()
```

#### 2. KDT 模式（Keyword Driven Testing）

关键字驱动模式，用例以 YAML 格式描述，通过关键字引擎动态执行，无需编写 Python 代码。

**示例：** [test_login.yaml](file:///d:/Faye/project/autotestskill/web_ui/test_cases/kdt/login/test_login.yaml)

```yaml
test_cases:
  - name: 登录成功-普通用户
    data:
      username: testuser
      password: test123
      nickname: 测试用户
    steps:
      - action: goto_login
      - action: input_username
        value: "{{ username }}"
      - action: input_password
        value: "{{ password }}"
      - action: click_login_button
      - action: assert_logged_in
        value: "{{ nickname }}"
```

#### 3. BDD 模式（Behavior Driven Development）

行为驱动模式，用自然语言（Gherkin）描述测试场景，产品经理也能看懂。

**示例：** [login.feature](file:///d:/Faye/project/autotestskill/web_ui/test_cases/bdd/features/login.feature)

```gherkin
Feature: 用户登录

  @smoke
  Scenario: 普通用户登录成功
    Given 用户打开登录页面
    When 用户输入用户名 "testuser" 和密码 "test123"
    And 用户点击登录按钮
    Then 应该跳转到首页
    And 应该显示欢迎信息包含 "测试用户"
```

### 快速开始

#### 1. 安装依赖

```bash
cd web_ui

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
# 如需支持更多浏览器：
playwright install firefox webkit
```

#### 2. 确保电商系统已启动

请先按照上方步骤启动 **mall-lite** 电商系统（默认监听 8000 端口）。

#### 3. 运行测试

项目提供了一键运行脚本 [run.py](file:///d:/Faye/project/autotestskill/web_ui/run.py)：

```bash
cd web_ui

# 查看帮助
python run.py

# ===== Pytest (POM/KDT) =====
python run.py smoke          # 运行冒烟测试
python run.py regression     # 运行回归测试
python run.py login          # 运行登录模块
python run.py search         # 运行搜索模块
python run.py cart           # 运行购物车模块
python run.py order          # 运行订单模块
python run.py e2e            # 运行端到端测试
python run.py all            # 运行全部用例
python run.py p0             # 运行 P0 优先级用例

# ===== Behave (BDD) =====
python run.py bdd            # 运行全部 BDD 用例
python run.py bdd-smoke      # 运行 BDD 冒烟测试
python run.py bdd-login      # 只运行登录 Feature
python run.py bdd-search     # 只运行搜索 Feature
python run.py bdd-cart       # 只运行购物车 Feature
python run.py bdd-e2e        # 只运行端到端 Feature
```

#### 4. Pytest 命令行直接运行

```bash
# 基础运行
pytest -v

# 指定浏览器
pytest --browser=firefox -v

# 有头模式（显示浏览器窗口）
pytest --headed=true -v

# 慢速模式（调试用，每次操作间隔 500ms）
pytest --slow-mo=500 -v

# 指定被测地址
pytest --base-url=http://localhost:8000 -v

# 指定环境（dev / staging / prod）
pytest --env=dev -v

# 运行带标记的用例
pytest -m "smoke and login" -v

# 并发执行（4 个进程）
pytest -n 4 -v

# 失败重试 2 次
pytest --reruns=2 -v

# 生成 Allure 报告数据
pytest --alluredir=reports/allure-results --clean-alluredir -v
```

### 测试报告

#### Allure 报告（推荐）

```bash
# 1. 运行测试并生成数据
pytest --alluredir=reports/allure-results --clean-alluredir

# 2. 安装 Allure（如未安装）
#    Windows:  scoop install allure
#    macOS:    brew install allure
#    Linux:    apt install allure

# 3. 启动报告服务
allure serve reports/allure-results

# 或：一键运行
python run.py report
```

报告特性：
- 📊 用例通过率统计
- 📸 失败自动截图附件
- 📝 详细步骤日志
- 📦 按模块 / 优先级分类
- 🔍 失败原因分类

#### pytest-html 报告

```bash
pytest --html=reports/report.html --self-contained-html
```

#### 日志文件

测试执行日志保存在：`web_ui/reports/test.log`

### 配置说明

#### 多环境配置

配置文件：[env_config.yaml](file:///d:/Faye/project/autotestskill/web_ui/config/env_config.yaml)

配置优先级（从高到低）：
1. 命令行参数（`--base-url`, `--browser` 等）
2. 环境变量（`MALLLITE_BASE_URL`, `MALLLITE_BROWSER` 等）
3. 配置文件（`env_config.yaml` 中对应环境）
4. 默认值（`Config.DEFAULTS`）

```bash
# 使用环境变量覆盖
set MALLLITE_BASE_URL=http://staging.example.com
set MALLLITE_BROWSER=firefox
pytest -v
```

#### 自定义 Pytest Markers

在 [pytest.ini](file:///d:/Faye/project/autotestskill/web_ui/pytest.ini) 中定义：

| Marker | 说明 |
|--------|------|
| `@pytest.mark.smoke` | 冒烟测试（核心功能，发布前必跑） |
| `@pytest.mark.regression` | 回归测试（全量） |
| `@pytest.mark.login` | 登录模块 |
| `@pytest.mark.search` | 搜索模块 |
| `@pytest.mark.product` | 商品模块 |
| `@pytest.mark.cart` | 购物车模块 |
| `@pytest.mark.order` | 订单模块 |
| `@pytest.mark.e2e` | 端到端测试 |
| `@pytest.mark.p0` | P0 最高优先级 |
| `@pytest.mark.p1` | P1 高优先级 |
| `@pytest.mark.p2` | P2 中优先级 |
| `@pytest.mark.kdt` | KDT 模式用例 |

### 核心 Fixture 说明

在 [conftest.py](file:///d:/Faye/project/autotestskill/web_ui/conftest.py) 中定义，可直接在测试用例中注入使用：

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `config` | session | 全局配置对象 |
| `browser_instance` | session | 共享浏览器实例 |
| `context` | function | 独立浏览器上下文 |
| `page` | function | Playwright Page 对象 |
| `login_page` | function | 登录页面对象 (POM) |
| `home_page` | function | 首页页面对象 (POM) |
| `product_page` | function | 商品详情页对象 (POM) |
| `cart_page` | function | 购物车页面对象 (POM) |
| `order_page` | function | 订单页面对象 (POM) |
| `profile_page` | function | 个人中心页面对象 (POM) |
| `admin_user` | function | 管理员测试账号 |
| `normal_user` | function | 普通用户测试账号 |
| `vip_user` | function | VIP 用户测试账号 |

---

## 四、完整工作流示例

```bash
# ===== 1. 启动电商系统 =====
cd mall-lite
pip install -r requirements.txt
python run.py
# 保持此终端运行，另开终端执行下面步骤

# ============================================
# ===== 2a. 运行 API 自动化测试（推荐先跑）=====
# ============================================
cd ../api
pip install -r requirements.txt

# 运行 API 冒烟测试（验证接口连通性）
pytest -m "smoke or p0"

# 运行 API 全量回归测试
pytest -m regression

# 查看 API Allure 报告
allure serve allure-results

# ============================================
# ===== 2b. 运行 Web UI 自动化测试 ===========
# ============================================
cd ../web_ui
pip install -r requirements.txt
playwright install chromium

# 运行冒烟测试（验证环境）
python run.py smoke

# 运行全量回归测试
python run.py all

# 查看 Allure 报告
python run.py report
```

---

## 五、常见问题

### Q: 浏览器无法启动？
A: 请确认已执行 `playwright install chromium` 安装浏览器内核。

### Q: 连接被拒绝 / 访问不到页面 / API 报 ConnectionError？
A: 请确认 mall-lite 电商系统已启动并监听 8000 端口。
- API 测试：确认 `http://localhost:8000/api/products` 能正常返回
- Web UI 测试：可通过 `--base-url` 参数指定地址

### Q: API 测试报 "登录失败"？
A: 请确认 mall-lite 使用的是预置数据（默认包含 admin/admin123 账号）。如果数据被修改过，重启 mall-lite 会自动恢复默认数据。

### Q: API 测试购物车用例偶尔失败？
A: 检查是否用例间数据污染——项目已配置 `autouse` 的 `clean_cart` fixture，每个用例前自动清空购物车。如仍有问题，检查是否有未使用 fixture 的用例直接操作购物车。

### Q: 如何在 CI/CD 中运行？
A:
**API 测试：**
```bash
cd api
pytest -m regression --alluredir=allure-results
```

**Web UI 测试：**
```bash
cd web_ui
pytest --headed=false --alluredir=reports/allure-results -v
```

### Q: 如何添加新的测试用例？
A:
**API 测试：**
- 在 `api/test_cases/` 下新建 `test_xxx.py`，注入 fixture 编写用例
- 新增接口：在 `api/api_objects/` 下继承 `ApiClient` 创建新的 API 类

**Web UI 测试：**
- **POM 模式**：在 `web_ui/test_cases/pom/` 下新建 `test_xxx.py`，注入页面对象 fixture 编写用例
- **KDT 模式**：在 `web_ui/test_cases/kdt/` 模块目录下新建 `test_xxx.yaml`，按格式编写步骤
- **BDD 模式**：在 `web_ui/test_cases/bdd/features/` 下新建 `.feature` 文件，并在 `steps/` 中实现对应步骤

---

## 六、测试覆盖范围

### API 自动化测试（api/）

| 模块 | 正向用例 | 反向用例 | 专项验证 | 覆盖内容 |
|------|---------|---------|---------|---------|
| 登录/注册 | ✅ | ✅ | ✅ | 成功/失败、Session共享、JWT模拟、密码错误、重复登录 |
| 商品 | ✅ | ✅ | ✅ | 列表/详情/分类/搜索、列表vs详情一致性、分页边界、分类筛选 |
| 购物车 | ✅ | ✅ | ✅ | 加购/修改/删除/清空、数量边界(0/负数/极大值)、总数量计算、跨用例自动清理 |
| 订单 | ✅ | ✅ | ✅ | 下单/列表/详情、空购物车下单、连续下单两次、金额小计之和=总金额、列表vs详情一致性 |
| 端到端链路 | ✅ | - | - | 新用户：注册→登录→搜索→加购→改数量→下单→查单；管理员链路 |
| 鉴权安全 | - | ✅ | ✅ | 未登录访问、登录失败无Session、新Session隔离、SQL注入/XSS输入 |
| 容错能力 | - | - | ✅ | 超时配置、5xx重试策略、POST不重试、并发加购/登录/下单 |
| Schema校验 | ✅ | - | ✅ | 登录/商品列表/详情/购物车/订单/分类 JSON Schema |
| 数据驱动 | ✅ | ✅ | - | YAML驱动(购物车/订单)、Excel驱动(登录多Sheet) |
| 分页验证 | ✅ | ✅ | - | 页码/页大小边界、超出范围、空页处理 |

### Web UI 自动化测试（web_ui/）

| 模块 | POM 用例 | KDT 用例 | BDD 场景 | 覆盖内容 |
|------|---------|---------|---------|---------|
| 登录 | ✅ | ✅ | ✅ | 成功/失败、权限验证 |
| 搜索 | ✅ | ✅ | ✅ | 关键字、分类、空结果 |
| 商品 | ✅ | - | - | 详情查看、价格展示 |
| 购物车 | ✅ | ✅ | ✅ | 添加、删除、数量修改 |
| 订单 | ✅ | ✅ | - | 下单、查看订单列表 |
| 端到端 | ✅ | - | ✅ | 完整购物流程 |

### 总体对比

| 维度 | API 测试 | Web UI 测试 |
|------|---------|------------|
| **执行速度** | ⚡ 极快（秒级/百条用例） | 🐢 较慢（浏览器渲染开销） |
| **稳定性** | ✅ 高（不受 UI 变更影响） | ⚠️ 中（受页面元素、渲染影响） |
| **覆盖层级** | 接口层（业务逻辑、数据） | UI 层（用户交互、视觉） |
| **适合场景** | 回归测试、边界/异常、并发、一致性 | 冒烟测试、E2E 流程、视觉验证 |
| **维护成本** | 低（接口稳定） | 中高（页面改版需更新定位器） |
| **技术栈** | Pytest + Requests | Pytest + Playwright (+Behave BDD) |
