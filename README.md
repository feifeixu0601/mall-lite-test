# MallLite 电商系统 & Web UI 自动化测试

本项目包含三大部分：

1. **mall-lite**：基于 FastAPI 的轻量级电商系统（被测系统）
2. **web_ui**：基于 Pytest + Playwright 的 Web UI 自动化测试框架，支持 POM / KDT / BDD 三种测试模式
3. **api**：基于 Pytest + Requests 的 API 接口自动化测试框架，支持 API 对象封装、数据驱动、JSON Schema 校验

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
├── web_ui/                    # Web UI 自动化测试框架
│   ├── common/                # 公共工具模块
│   │   ├── logger.py          # 日志封装
│   │   ├── screenshot.py      # 截图工具
│   │   ├── allure_helper.py   # Allure 报告辅助
│   │   ├── data_reader.py     # 测试数据读取（YAML/JSON/CSV）
│   │   └── random_data.py     # 随机数据生成
│   ├── config/                # 配置管理
│   │   ├── config.py          # 多环境配置类
│   │   └── env_config.yaml    # 环境配置文件（dev/staging/prod）
│   ├── engine/                # 测试引擎
│   │   └── test_engine.py     # KDT 关键字驱动引擎
│   ├── keywords/              # KDT 关键字库
│   │   ├── base_keywords.py   # 基础关键字
│   │   ├── login_keywords.py  # 登录关键字
│   │   ├── search_keywords.py # 搜索关键字
│   │   ├── cart_keywords.py   # 购物车关键字
│   │   ├── order_keywords.py  # 订单关键字
│   │   └── keyword_registry.py# 关键字注册中心
│   ├── pages/                 # POM 页面对象
│   │   ├── base_page.py       # 基础页面类
│   │   ├── login_page.py      # 登录页
│   │   ├── home_page.py      # 首页
│   │   ├── product_page.py    # 商品详情页
│   │   ├── cart_page.py       # 购物车页
│   │   ├── order_page.py      # 订单页
│   │   └── profile_page.py    # 个人中心页
│   ├── test_cases/            # 测试用例（三种模式）
│   │   ├── pom/               # POM 模式用例
│   │   ├── kdt/               # KDT 关键字驱动用例（YAML）
│   │   └── bdd/               # BDD 行为驱动用例
│   │       ├── features/      # .feature 场景文件
│   │       └── steps/         # 步骤定义
│   ├── test_data/             # 测试数据文件（YAML/JSON/CSV）
│   ├── reports/               # 测试报告输出目录
│   ├── conftest.py            # Pytest 全局配置 & Fixtures
│   ├── pytest.ini             # Pytest 配置文件
│   ├── behave.ini             # Behave (BDD) 配置文件
│   ├── allure_config.py       # Allure 报告配置生成
│   ├── requirements.txt       # 测试框架依赖
│   └── run.py                 # 测试一键运行脚本
│
└── api/                       # API 接口自动化测试框架
    ├── api_objects/           # API 对象层（类似 POM）
    │   ├── base_api.py        # 基础 API 客户端（自动重试、超时、日志）
    │   ├── user_api.py        # 用户接口（登录/注册）
    │   ├── product_api.py     # 商品接口
    │   ├── cart_api.py        # 购物车接口
    │   └── order_api.py       # 订单接口
    ├── common/                # 公共工具模块
    │   ├── logger.py          # 日志封装
    │   ├── assertions.py      # 接口断言工具（链式断言）
    │   ├── data_reader.py     # 测试数据读取（YAML/JSON/Excel）
    │   ├── extractor.py       # 响应数据提取器
    │   ├── schemas.py         # JSON Schema 定义与校验
    │   └── response_validator.py # 响应校验器
    ├── test_cases/            # 测试用例
    │   ├── test_auth.py       # 鉴权测试
    │   ├── test_user.py       # 用户模块
    │   ├── test_product.py    # 商品模块
    │   ├── test_cart.py       # 购物车模块
    │   ├── test_order.py      # 订单模块
    │   ├── test_shopping_flow.py # 购物流程端到端
    │   ├── test_schema_auto.py     # Schema 校验
    │   ├── test_session.py     # Session 管理
    │   ├── test_pagination.py  # 分页测试
    │   ├── test_data_consistency.py # 数据一致性
    │   ├── test_edge_cases.py  # 边界用例
    │   ├── test_resilience.py  # 容错/重试
    │   ├── test_yaml_drive.py  # YAML 数据驱动
    │   ├── test_excel_drive.py # Excel 数据驱动
    │   ├── test_extractor_practice.py # 提取器练习
    │   └── test_allure_demo.py # Allure 报告演示
    ├── test_data/             # 测试数据文件
    │   ├── login_cases.json   # 登录用例（JSON）
    │   ├── login_cases.xlsx   # 登录用例（Excel）
    │   ├── product_cases.json  # 商品用例（JSON）
    │   ├── cart_cases.yaml   # 购物车用例（YAML）
    │   └── order_cases.yaml    # 订单用例（YAML）
    ├── examples/              # 示例代码
    │   ├── sign_demo.py       # 签名算法示例
    │   └── mock_demo.py       # Mock 示例
    ├── tools/                 # 工具脚本
    │   └── create_excel.py    # Excel 数据生成
    ├── reports/             # 报告 & 日志输出
    ├── conftest.py            # Pytest 全局配置 & Fixtures
    ├── pytest.ini             # Pytest 配置文件
    ├── requirements.txt       # 依赖清单
    └── testrequests.py        # Requests 基础用法示例
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

## 二、Web UI 自动化测试 (web_ui)

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

## 三、API 接口自动化测试 (api)

### 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Requests | 2.32.3 | HTTP 请求库 |
| Pytest | 8.3.4 | 测试运行框架 |
| Allure-Pytest | 2.13.5 | Allure 测试报告 |
| JSON Schema | 4.23.0 | JSON Schema 校验 |
| PyYAML | 6.0.2 | YAML 解析 |
| openpyxl | - | Excel 数据读取 |

### 框架架构

#### 1. API 对象层 (api_objects)

类似 Web UI 的 POM 模式，将每个业务模块的接口封装到独立的 API 类中，用例代码简洁易维护。

- **[base_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/base_api.py)**：基础 API 客户端
  - 自动重试（5xx 错误重试 2 次，带退避间隔）
  - 可配置超时（默认 10 秒）
  - 统一请求/响应日志格式
  - Session 安全管理
- **[user_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/user_api.py)**：用户接口（登录/注册）
- **[product_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/product_api.py)**：商品接口
- **[cart_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/cart_api.py)**：购物车接口
- **[order_api.py](file:///d:/Faye/project/autotestskill/api/api_objects/order_api.py)**：订单接口

**示例：**

```python
# 登录并共享 Session
user = UserApi("http://localhost:8000")
session = user.login_and_share("admin", "admin123")

# 购物车接口复用登录 Session
cart = CartApi("http://localhost:8000")
cart.session = session
resp = cart.add_to_cart(product_id=1, quantity=2)
```

#### 2. 链式断言工具 (assertions)

针对 MallLite 统一返回格式（HTTP 200 + body.code）封装的断言工具，支持链式调用。

**示例：** [test_auth.py](file:///d:/Faye/project/autotestskill/api/test_cases/test_auth.py)

```python
resp = user_api.login("admin", "admin123")
a = ApiAssertions(resp)

a.assert_success()                        # code == 200
a.assert_message("登录成功")               # message 包含文本
a.assert_has_field("data.username")        # 字段存在
a.assert_field_value("data.role", "admin") # 字段值
a.assert_schema("login")                   # JSON Schema 校验
a.assert_response_time(2)                  # 响应时间 <= 2s
```

#### 3. Fixture 设计

在 [conftest.py](file:///d:/Faye/project/autotestskill/api/conftest.py) 中定义，核心设计：

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `admin_session` | session | 管理员登录 Session，整个测试会话只登录一次 |
| `user_api` | function | 用户 API（未登录） |
| `product_api` | function | 商品 API（无需登录） |
| `cart_api` | function | 购物车 API（未登录） |
| `order_api` | function | 订单 API（未登录） |
| `admin_user_api` | function | 已登录的用户 API（共享 admin_session） |
| `admin_cart_api` | function | 已登录的购物车 API（共享 admin_session） |
| `admin_order_api` | function | 已登录的订单 API（共享 admin_session） |
| `created_order` | function | 链式 Fixture：自动加购物车并创建订单，返回 order_no |
| `first_product` | function | 链式 Fixture：获取第一个商品的完整信息 |
| `assert_api` | function | 断言工具类 |
| `clean_cart` | function | 自动清理（autouse）：每个用例前清空购物车 |
| `unique_username` | function | 生成唯一用户名（时间戳），用于注册测试 |

### 数据驱动

支持三种数据驱动方式：

#### YAML 驱动
```python
# 读取 cart_cases.yaml 中的用例
@pytest.mark.parametrize("case", load_yaml("test_data/cart_cases.yaml"))
def test_cart_yaml_driven(case, admin_cart_api, assert_api):
    resp = admin_cart_api.add_to_cart(**case["input"])
    assert_api(resp).assert_code(case["expected_code"])
```

#### JSON 驱动
```python
# 读取 login_cases.json 中的用例
@pytest.mark.parametrize("case", load_json("test_data/login_cases.json"))
def test_login_json_driven(case, user_api, assert_api):
    resp = user_api.login(case["username"], case["password"])
    assert_api(resp).assert_code(case["expected_code"])
```

#### Excel 驱动
```python
# 读取 login_cases.xlsx 中的用例
@pytest.mark.parametrize("case", load_excel("test_data/login_cases.xlsx", "Sheet1"))
def test_login_excel_driven(case, user_api, assert_api):
    resp = user_api.login(case["username"], case["password"])
    assert_api(resp).assert_code(case["expected_code"])
```

### 快速开始

#### 1. 安装依赖

```bash
cd api

# 安装 Python 依赖
pip install -r requirements.txt
```

#### 2. 确保电商系统已启动

请先启动 **mall-lite** 电商系统（默认监听 8000 端口）。

#### 3. 运行测试

```bash
# 运行全部用例
pytest -v

# 运行冒烟测试
pytest -m smoke -v

# 运行指定模块
pytest -m login -v
pytest -m cart -v
pytest -m order -v

# 运行 P0 优先级
pytest -m p0 -v

# 生成 Allure 报告数据
pytest --alluredir=allure-results --clean-alluredir -v
```

#### 4. Pytest 自定义 Markers

在 [pytest.ini](file:///d:/Faye/project/autotestskill/api/pytest.ini) 中定义：

| Marker | 说明 |
|--------|------|
| `@pytest.mark.smoke` | 冒烟测试 |
| `@pytest.mark.regression` | 回归测试 |
| `@pytest.mark.login` | 登录接口 |
| `@pytest.mark.register` | 注册接口 |
| `@pytest.mark.product` | 商品接口 |
| `@pytest.mark.category` | 分类接口 |
| `@pytest.mark.cart` | 购物车接口 |
| `@pytest.mark.order` | 订单接口 |
| `@pytest.mark.positive` | 正向用例 |
| `@pytest.mark.negative` | 反向用例 |
| `@pytest.mark.schema` | Schema 校验用例 |
| `@pytest.mark.p0` | 最高优先级 |
| `@pytest.mark.p1` | 高优先级 |
| `@pytest.mark.p2` | 中优先级 |

### 测试报告

#### Allure 报告（推荐）

```bash
# 1. 运行测试并生成数据
pytest --alluredir=allure-results --clean-alluredir

# 2. 启动报告服务
allure serve allure-results
```

报告特性：
- 📊 用例通过率统计
- 📝 请求/响应日志自动附加
- 🔍 失败用例自动附加错误堆栈
- 📦 按模块 / 优先级分类

#### 日志文件

测试执行日志保存在：`api/reports/logs/api_test.log`（按日期分割）

### 核心能力一览

| 能力 | 说明 | 示例文件 |
|------|------|---------|
| Session 共享登录 | 整个会话只登录一次，节省时间 | `admin_session` fixture |
| 自动重试 | 5xx 错误自动重试 2 次，退避间隔 | `base_api.py` Retry 策略 |
| 自动清理 | 每个用例前清空购物车，避免数据污染 | `clean_cart` autouse fixture |
| 链式断言 | 一行代码完成多维度校验 | `test_auth.py` |
| JSON Schema 校验 | 响应结构一致性校验 | `test_schema_auto.py` |
| 数据驱动 | YAML / JSON / Excel 三种格式 | `test_yaml_drive.py` / `test_excel_drive.py` |
| 链式 Fixture | 自动前置依赖（创建订单、获取商品） | `created_order` / `first_product` |
| 容错/重试 | 接口异常场景覆盖 | `test_resilience.py` |
| 边界值测试 | 参数边界、异常输入覆盖 | `test_edge_cases.py` |
| 数据一致性 | 写操作后读校验 | `test_data_consistency.py` |
| 分页测试 | 分页参数、边界校验 | `test_pagination.py` |
| 鉴权测试 | 登录/未登录状态对比 | `test_auth.py` |
| 端到端流程 | 登录→加购物车→下单→查订单 | `test_shopping_flow.py` |

---

## 四、完整工作流示例

```bash
# ===== 1. 启动电商系统 =====
cd mall-lite
pip install -r requirements.txt
python run.py
# 保持此终端运行，另开一个终端执行下面步骤

# ===== 2. 准备测试环境 =====
cd ../web_ui
pip install -r requirements.txt
playwright install chromium

# ===== 3. 运行冒烟测试（验证环境） =====
python run.py smoke

# ===== 4. 运行全量回归测试 =====
python run.py all

# ===== 5. 查看 Allure 报告 =====
python run.py report
```

---

## 五、常见问题

### Q: 浏览器无法启动？
A: 请确认已执行 `playwright install chromium` 安装浏览器内核。

### Q: 连接被拒绝 / 访问不到页面？
A: 请确认 mall-lite 电商系统已启动并监听 8000 端口。可通过 `--base-url` 参数指定地址。

### Q: 如何在 CI/CD 中运行？
A: 使用无头模式 + 指定输出目录：
```bash
pytest --headed=false --alluredir=reports/allure-results -v
```

### Q: 如何添加新的测试用例？
A:
- **POM 模式**：在 `test_cases/pom/` 下新建 `test_xxx.py`，注入页面对象 fixture 编写用例
- **KDT 模式**：在 `test_cases/kdt/` 模块目录下新建 `test_xxx.yaml`，按格式编写步骤
- **BDD 模式**：在 `test_cases/bdd/features/` 下新建 `.feature` 文件，并在 `steps/` 中实现对应步骤
- **API 模式**：在 `api/test_cases/` 下新建 `test_xxx.py`，注入 API fixture 编写用例，或在 `api/test_data/` 添加数据文件使用数据驱动

---

## 六、测试覆盖范围

### Web UI 测试覆盖

| 模块 | POM 用例 | KDT 用例 | BDD 场景 | 覆盖内容 |
|------|---------|---------|---------|---------|
| 登录 | ✅ | ✅ | ✅ | 成功/失败、权限验证 |
| 搜索 | ✅ | ✅ | ✅ | 关键字、分类、空结果 |
| 商品 | ✅ | - | - | 详情查看、价格展示 |
| 购物车 | ✅ | ✅ | ✅ | 添加、删除、数量修改 |
| 订单 | ✅ | ✅ | - | 下单、查看订单列表 |
| 端到端 | ✅ | - | ✅ | 完整购物流程 |

### API 接口测试覆盖

| 模块 | 用例文件 | 覆盖内容 |
|------|---------|---------|
| 鉴权 | test_auth.py | 登录响应、密码错误无 Session、Session 隔离性、JWT 使用模式演示 |
| 用户 | test_user.py | 登录成功/失败、注册成功/失败、参数校验 |
| 商品 | test_product.py | 商品列表、详情、分类、分页、搜索 |
| 购物车 | test_cart.py | 添加、删除、修改数量、清空、边界值 |
| 订单 | test_order.py | 创建订单、查看订单列表、订单详情 |
| 购物流程 | test_shopping_flow.py | 登录→加购物车→下单→查订单 完整流程 |
| Schema | test_schema_auto.py | 各接口响应 JSON Schema 结构校验 |
| Session | test_session.py | Cookie 管理、Session 共享与隔离 |
| 分页 | test_pagination.py | 分页参数、边界、空页 |
| 数据一致性 | test_data_consistency.py | 写后读校验、数据关联一致性 |
| 边界值 | test_edge_cases.py | 参数边界、异常输入、空值处理 |
| 容错/重试 | test_resilience.py | 接口异常、超时、重试策略 |
| 数据驱动 | test_yaml_drive.py / test_excel_drive.py | YAML / JSON / Excel 三种数据驱动方式 |
| 提取器 | test_extractor_practice.py | 响应数据提取、关联参数传递 |
| Allure | test_allure_demo.py | Allure 报告特性演示（步骤、附件） |
