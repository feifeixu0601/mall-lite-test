# MallLite 电商系统 & Web UI 自动化测试

本项目包含两大部分：

1. **mall-lite**：基于 FastAPI 的轻量级电商系统（被测系统）
2. **web_ui**：基于 Pytest + Playwright 的 Web UI 自动化测试框架，支持 POM / KDT / BDD 三种测试模式

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

## 三、完整工作流示例

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

## 四、常见问题

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

---

## 五、测试覆盖范围

| 模块 | POM 用例 | KDT 用例 | BDD 场景 | 覆盖内容 |
|------|---------|---------|---------|---------|
| 登录 | ✅ | ✅ | ✅ | 成功/失败、权限验证 |
| 搜索 | ✅ | ✅ | ✅ | 关键字、分类、空结果 |
| 商品 | ✅ | - | - | 详情查看、价格展示 |
| 购物车 | ✅ | ✅ | ✅ | 添加、删除、数量修改 |
| 订单 | ✅ | ✅ | - | 下单、查看订单列表 |
| 端到端 | ✅ | - | ✅ | 完整购物流程 |
