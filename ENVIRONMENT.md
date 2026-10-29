# 环境搭建与配置手册（ENVIRONMENT.md）

本文档用于**从 GitHub 克隆代码后，从零重建一套可运行的环境**。

项目介绍、功能说明、用例清单见 [README.md](README.md)；本文档只解决一件事：**换机器 / 删掉本地代码重新拉取后，如何把三个模块跑起来**。

命令全部按 **Windows PowerShell** 编写，可直接复制执行。

---

## 一、适用范围

本项目包含三个独立模块，各自有独立的虚拟环境和依赖，必须分别安装：

| 模块 | 角色 | 虚拟环境目录 | 运行入口 |
|------|------|-------------|---------|
| `mall-lite/` | 被测系统（FastAPI 后端 + 页面） | `mall-lite/venv/` | `python run.py` |
| `api/` | 接口自动化测试（Pytest + Requests） | `api/.venv/` | `pytest` |
| `web_ui/` | UI 自动化测试（Pytest + Playwright + Behave） | `web_ui/venv/` | `python run.py` |

**模块间依赖关系**：`api` 和 `web_ui` 都依赖 `mall-lite` 提供后端服务（默认 `http://localhost:8000`）。
**`mall-lite` 未启动时，另外两个模块的测试会全部失败。**

---

## 二、环境基线清单（本机实测值）

### 2.1 基础环境

| 项目 | 实测值 | 说明 |
|------|--------|------|
| 操作系统 | Windows 10 / 11 | 命令按 PowerShell 语法 |
| Python（mall-lite、web_ui 用） | **3.13.12**，路径 `D:\Python\python-3.13.12` | 这两个模块的 venv 均由它创建 |
| Python（api 用） | **3.14.0**，路径 `C:\Users\51338\AppData\Local\Programs\Python\Python314` | `api/.venv` 由它创建 |
| Allure CLI | **2.45.0**，路径 `D:\tools\allure-2.45.0\bin` | 生成/查看报告用，需加入 PATH |
| Java 运行环境 | 必须存在 | Allure CLI 运行报告服务依赖 Java（JRE / JDK 均可） |
| Playwright 浏览器内核 | `chromium` | 由 `playwright install chromium` 安装 |
| 后端服务端口 | **8000** | 修改端口需同步改测试配置 |

> **建议**：统一使用 Python 3.13.12 创建三个虚拟环境，避免 `api/.venv`（3.14.0）与其它模块不一致带来的第三方库兼容问题。

### 2.2 依赖清单

#### mall-lite（`mall-lite/requirements.txt`，共 5 项）

| 包 | 版本 |
|----|------|
| fastapi | 0.109.0 |
| uvicorn | 0.27.0 |
| jinja2 | 3.1.3 |
| python-multipart | 0.0.6 |
| pyyaml | 6.0.1 |

#### api（`api/requirements.txt`，共 5 项）

| 包 | 版本 | 备注 |
|----|------|------|
| requests | 2.32.3 | |
| pytest | 8.3.4 | |
| allure-pytest | 2.13.5 | 与 web_ui 的 2.16.0 不一致 |
| jsonschema | 4.23.0 | |
| pyyaml | 6.0.2 | |
| **openpyxl** | **3.1.5（清单缺失，需手动补装）** | `test_excel_drive.py` 读取 `.xlsx` 时必需 |

#### web_ui（`web_ui/requirements.txt`，共 12 项）

| 包 | 版本 | 包 | 版本 |
|----|------|----|------|
| playwright | 1.49.1 | openpyxl | 3.1.5 |
| pytest | 8.3.4 | python-dotenv | 1.0.1 |
| pytest-html | 4.1.1 | pytest-xdist | 3.5.0 |
| allure-pytest | 2.16.0 | pytest-rerunfailures | 14.0 |
| pyyaml | 6.0.2 | pytest-ordering | 0.6 |
| behave | 1.3.3 | allure-behave | 2.16.0 |

---

## 三、目录职责速查

克隆后请先分清「必须保留的源码/数据」和「可随时删除的生成物」。

### 必须存在（缺失会导致运行失败）

| 路径 | 说明 |
|------|------|
| `mall-lite/app/` | 后端源码（`main.py` 为入口） |
| `mall-lite/data/*.json` | 运行时数据：`carts / categories / config / orders / products / users`（共 6 个），被 `DataStore("data")` 读取，**缺失会启动报错** |
| `mall-lite/templates/`、`mall-lite/static/` | 页面模板与样式 |
| `api/api_objects/`、`api/common/` | API 对象层与工具库 |
| `api/test_cases/` | 测试用例 |
| `api/test_data/` | 数据驱动用例的数据文件（YAML / Excel / JSON），缺失会导致对应用例报 `FileNotFoundError` |
| `api/conftest.py`、`api/pytest.ini` | Fixture 与 Pytest 配置 |
| `web_ui/common/`、`config/`、`pages/`、`keywords/`、`engine/` | 框架代码 |
| `web_ui/test_cases/`（`pom` / `kdt` / `bdd`） | 三种模式的用例 |
| `web_ui/test_data/` | 测试数据 |
| `web_ui/conftest.py`、`pytest.ini`、`behave.ini` | 配置 |

### 生成物（可随时删除，重新运行会再生）

| 路径 | 说明 |
|------|------|
| `api/allure-results/` | API 测试 Allure 报告数据 |
| `api/reports/logs/` | API 测试日志 `api_YYYY-MM-DD.log` |
| `web_ui/reports/` | UI 报告、日志 `test.log`、失败截图 `screenshots/` |
| `mall-lite/logs/` | 后端日志 `malllite_*.log` |
| 任意 `__pycache__/` | Python 字节码缓存 |

### 不纳入版本控制（克隆后需重建）

`mall-lite/venv/`、`api/.venv/`、`web_ui/venv/` —— 三个虚拟环境都不会随仓库下载，必须按下节步骤重建。

---

## 四、从零搭建步骤

> 以下命令假设仓库克隆到 `D:\Faye\project\autotestskill`，请按实际路径替换。

### 步骤 0：克隆仓库

```powershell
cd D:\Faye\project
git clone <你的仓库地址> autotestskill
cd autotestskill
```

### 步骤 1：创建 mall-lite 虚拟环境并安装依赖

```powershell
cd D:\Faye\project\autotestskill\mall-lite

# 创建虚拟环境
python -m venv venv

# 激活（若提示脚本被禁止执行，先执行下一行的临时策略设置）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

# 升级 pip 并安装依赖
python -m pip install --upgrade pip
pip install -r requirements.txt

# 验证
python -c "import fastapi, uvicorn; print('mall-lite 依赖 OK')"

# 退出虚拟环境
deactivate
```

### 步骤 2：创建 api 虚拟环境并安装依赖

```powershell
cd D:\Faye\project\autotestskill\api

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

# 重要：requirements.txt 缺少 openpyxl，Excel 数据驱动用例需要它
pip install openpyxl==3.1.5

# 验证
python -c "import requests, pytest, jsonschema, yaml, openpyxl; print('api 依赖 OK')"

deactivate
```

### 步骤 3：创建 web_ui 虚拟环境并安装依赖

```powershell
cd D:\Faye\project\autotestskill\web_ui

python -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

# 安装浏览器内核（必须，否则用例无法启动浏览器）
python -m playwright install chromium

# 验证
python -c "import playwright, behave, allure; print('web_ui 依赖 OK')"

deactivate
```

### 步骤 4：安装并验证 Allure CLI

若本机已有 Allure（如 `D:\tools\allure-2.45.0`），只需确保 `bin` 目录在 PATH 中：

```powershell
# 查看是否可用
allure --version

# 若找不到命令，临时加入 PATH（按实际安装路径替换）
$env:Path += ";D:\tools\allure-2.45.0\bin"
allure --version
```

若尚未安装：Windows 可用 `scoop install allure`，或从 Allure 官方发布页下载压缩包解压后手动加入 PATH。
**注意：Allure 运行报告服务需要 Java 环境**，请确认 `java -version` 可正常输出版本号。

### 步骤 5：环境自检

```powershell
# 1) 后端数据文件是否齐全（应输出 6 个文件）
Get-ChildItem D:\Faye\project\autotestskill\mall-lite\data

# 2) 三个虚拟环境解释器是否可用
D:\Faye\project\autotestskill\mall-lite\venv\Scripts\python.exe --version
D:\Faye\project\autotestskill\api\.venv\Scripts\python.exe --version
D:\Faye\project\autotestskill\web_ui\venv\Scripts\python.exe --version

# 3) Allure 是否可用
allure --version
```

---

## 五、启动与运行顺序

### 5.1 第一步：启动后端（必须最先启动）

**必须在 `mall-lite` 目录下启动**，因为后端使用相对路径读取 `data/` 和 `static/`，在其它目录启动会报文件找不到。

```powershell
cd D:\Faye\project\autotestskill\mall-lite
.\venv\Scripts\Activate.ps1
python run.py
```

启动成功后终端会输出：

```
  访问地址：http://localhost:8000
  API 文档：http://localhost:8000/docs
```

**自检**（另开一个终端）：

```powershell
# 方式一
curl.exe http://localhost:8000/api/products

# 方式二（PowerShell 原生）
Invoke-RestMethod http://localhost:8000/api/products | ConvertTo-Json -Depth 3
```

能返回包含 `code` 和 `data` 的 JSON，即表示后端正常。**保持该终端不关闭**，后续测试都要依赖它。

> 浏览器访问 http://localhost:8000/docs 可打开 FastAPI 自动生成的接口文档，用于人工核对接口。

### 5.2 第二步：运行 API 自动化测试

```powershell
cd D:\Faye\project\autotestskill\api
.\.venv\Scripts\Activate.ps1

# 冒烟：核心链路（建议每次先跑这个验证环境）
pytest -m "smoke or p0"

# 回归：全量
pytest -m regression

# 按模块
pytest -m login
pytest -m cart
pytest -m order
pytest -m product

# 按用例性质
pytest -m positive
pytest -m negative

# 单文件 / 单用例
pytest test_cases/test_shopping_flow.py -v
pytest "test_cases/test_shopping_flow.py::TestShoppingFlow::test_new_user_full_flow" -v
```

> 不激活虚拟环境时，可直接调用解释器：
> `D:\Faye\project\autotestskill\api\.venv\Scripts\python.exe -m pytest -m smoke`
> **注意：必须在 `api` 目录下执行**，否则 `pytest.ini` 的 `testpaths` 和模块导入会失效。

### 5.3 第三步：运行 Web UI 自动化测试

```powershell
cd D:\Faye\project\autotestskill\web_ui
.\venv\Scripts\Activate.ps1

python run.py smoke          # 冒烟
python run.py regression     # 回归
python run.py login          # 登录模块
python run.py search         # 搜索模块
python run.py cart           # 购物车模块
python run.py order          # 订单模块
python run.py e2e            # 端到端
python run.py all            # 全部
python run.py p0             # P0 优先级
```

常用命令行参数（直接执行 `pytest` 时）：

```powershell
pytest --headed=true -v              # 显示浏览器窗口
pytest --slow-mo=500 -v              # 每步间隔 500ms，便于观察
pytest --browser=firefox -v          # 指定浏览器（需已安装对应内核）
pytest --base-url=http://localhost:8000 -v   # 指定被测地址
pytest --env=dev -v                  # 指定环境（dev / staging / prod）
```

### 5.4 BDD（Behave）用例

```powershell
cd D:\Faye\project\autotestskill\web_ui
.\venv\Scripts\Activate.ps1

python run.py bdd            # 全部 BDD
python run.py bdd-smoke      # 只跑 @smoke 标签
python run.py bdd-login      # 只跑登录 Feature
python run.py bdd-report     # 跑 BDD 并生成 Allure 报告
```

### 5.5 生成并查看测试报告

两个模块的报告数据目录**不同**，注意区分：

```powershell
# ===== API 测试报告 =====
cd D:\Faye\project\autotestskill\api
allure serve allure-results

# ===== Web UI 测试报告 =====
cd D:\Faye\project\autotestskill\web_ui
allure serve reports/allure-results

# 或使用一键脚本（内部会自动跑一次测试再打开报告）
python run.py report
```

| 模块 | 报告数据目录 | 文本日志位置 |
|------|-------------|-------------|
| mall-lite | 无 | `mall-lite/logs/malllite_YYYY-MM-DD.log` |
| api | `api/allure-results/` | `api/reports/logs/api_YYYY-MM-DD.log` |
| web_ui | `web_ui/reports/allure-results/` | `web_ui/reports/test.log`，截图在 `web_ui/reports/screenshots/` |

---

## 六、环境变量与配置

### 6.1 web_ui：支持环境变量覆盖

配置优先级（从高到低）：

1. 命令行参数（`--base-url`、`--browser`、`--headed`、`--slow-mo`）
2. 环境变量（下表）
3. 配置文件 `web_ui/config/env_config.yaml` 中对应环境的配置
4. 代码内置默认值（`web_ui/config/config.py` 的 `Config.DEFAULTS`）

支持的环境变量（前缀固定为 `MALLLITE_`）：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `MALLLITE_BASE_URL` | `http://localhost:8000` | 被测系统地址 |
| `MALLLITE_BROWSER` | `chromium` | `chromium` / `firefox` / `webkit` |
| `MALLLITE_HEADLESS` | `True` | 是否无头模式（`true` / `false`） |
| `MALLLITE_SLOW_MO` | `0` | 每步操作间隔（毫秒） |
| `MALLLITE_TIMEOUT` | `10000` | 默认超时（毫秒） |
| `MALLLITE_VIEWPORT_WIDTH` | `1280` | 视口宽度 |
| `MALLLITE_VIEWPORT_HEIGHT` | `720` | 视口高度 |
| `MALLLITE_SCREENSHOT_ON_FAILURE` | `True` | 失败自动截图 |
| `MALLLITE_VIDEO_ON_FAILURE` | `False` | 失败录制视频 |
| `MALLLITE_RETRY_COUNT` | `0` | 失败重试次数 |
| `MALLLITE_PAGE_SIZE` | `10` | 默认分页大小 |

PowerShell 中临时设置（只对当前终端会话有效）：

```powershell
$env:MALLLITE_BASE_URL = "http://staging.example.com"
$env:MALLLITE_BROWSER = "firefox"
$env:MALLLITE_HEADLESS = "false"
pytest -v
```

多环境配置文件：`web_ui/config/env_config.yaml`，内置 `dev` / `staging` / `prod` 三个环境，通过 `--env=dev` 切换。

### 6.2 api：地址为代码内配置

`api` 模块**没有**环境变量机制，被测地址写在代码中，默认 `http://localhost:8000`：

- 统一入口：`api/conftest.py` 中的 `BASE_URL = "http://localhost:8000"`
- 部分用例内部也会直接写死该地址（例如端到端链路用例）

若后端地址变更，需要修改 `conftest.py` 及局部硬编码处。

### 6.3 配置文件位置汇总

| 文件 | 作用 |
|------|------|
| `api/pytest.ini` | api 的用例目录、默认参数、自定义标记 |
| `web_ui/pytest.ini` | web_ui 的用例目录、默认参数、标记、日志配置 |
| `web_ui/behave.ini` | BDD 运行配置 |
| `web_ui/config/env_config.yaml` | web_ui 多环境地址 |
| `web_ui/config/config.py` | web_ui 默认值与配置优先级实现 |

---

## 七、测试账号与数据文件

### 7.1 预置测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| testuser | test123 | 普通用户 |
| vipuser | vip123 | VIP 用户 |

自动化用例中主要使用 `admin`（需登录的 fixture 默认用它）和 `testuser`。

### 7.2 数据文件清单

| 路径 | 数量 | 说明 |
|------|------|------|
| `mall-lite/data/` | 6 个 JSON | `carts` / `categories` / `config` / `orders` / `products` / `users`，后端运行时读写 |
| `mall-lite/backup/` | 按日期分目录 | 数据备份快照（同样 6 个 JSON） |
| `api/test_data/` | 6 个 | `cart_cases.yaml`、`order_cases.yaml`、`login_cases.json`、`product_cases.json`、`login_cases.xlsx`、`__init__.py` |
| `web_ui/test_data/` | 10 个 | 登录 / 搜索 / 购物车 / 分类等 YAML、JSON、CSV 数据文件 |

### 7.3 数据被改坏后如何重置

测试过程中会不断往购物车、订单写入数据，导致 `mall-lite/data/` 下的 JSON 被修改。若出现「账号登不上」「商品数据异常」等现象，按以下方式恢复：

**方式一：用备份覆盖（推荐）**

```powershell
cd D:\Faye\project\autotestskill\mall-lite
# 先停止后端服务，再执行备份覆盖（备份目录名按实际日期替换）
Copy-Item .\backup\20260811_173442\*.json .\data\ -Force
```

**方式二：重新生成基础数据**

`mall-lite/generate_data.py` 可重新生成分类、商品、用户等基础数据：

```powershell
cd D:\Faye\project\autotestskill\mall-lite
.\venv\Scripts\Activate.ps1
python generate_data.py
```

> 注意：该脚本会重写 `data/` 下的基础数据，执行前建议先备份当前 `data/` 目录。

---

## 八、故障排查表

| 症状 | 原因 | 解决 |
|------|------|------|
| `ConnectionError` / `Connection refused` / 浏览器打不开页面 | 后端未启动或端口不是 8000 | 按 5.1 启动 `mall-lite`，用 `curl.exe http://localhost:8000/api/products` 自检 |
| 后端启动报找不到 `data` 或 `static` | 在错误目录下启动了 `run.py` | 必须在 `mall-lite` 目录内执行 `python run.py` |
| 用例断言「登录失败」 | `mall-lite/data/users.json` 被改动，预置账号丢失 | 按 7.3 重置数据 |
| 购物车类用例断言失败 | 上一条用例残留数据污染 | 框架已配置 `autouse` 的 `clean_cart` fixture 自动清空；若仍失败，检查是否有用例绕过 fixture 直接操作购物车 |
| `ModuleNotFoundError: No module named 'api_objects'` 等 | 未在对应模块目录下执行，或虚拟环境未激活 | 切到 `api`（或 `web_ui`）目录，激活对应虚拟环境后再执行 |
| `FileNotFoundError: 数据文件不存在` | `test_data/` 下数据文件缺失 | 确认仓库中 `api/test_data/`、`web_ui/test_data/` 文件齐全 |
| Excel 驱动用例报 `ModuleNotFoundError: openpyxl` | `api/requirements.txt` 未包含 openpyxl | 执行 `pip install openpyxl==3.1.5` |
| 浏览器无法启动 / `Executable doesn't exist` | 未安装 Playwright 内核 | 在 web_ui 虚拟环境中执行 `python -m playwright install chromium` |
| `allure` 不是内部或外部命令 | Allure CLI 未安装或未加入 PATH | 按步骤 4 配置 PATH，`allure --version` 验证 |
| `allure serve` 报 Java 相关错误 | 本机缺少 Java 运行环境 | 安装 JRE / JDK，`java -version` 验证 |
| PowerShell 无法执行 `Activate.ps1` | 脚本执行策略限制 | 先执行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `test_resilience.py` 中极短超时用例未触发超时 | Windows + localhost 下 TCP 连接极快，`timeout=0.001` 不可靠 | 属于已知平台限制，用例已标记为 `xfail`，在远程/CI 环境会正常触发 |

---

## 九、已知问题（实测，需留意）

1. **仓库存在生成物污染**：由于项目根目录缺少 `.gitignore`，当前版本控制中包含大量生成文件——`api/allure-results/` 约 1786 个、`__pycache__` 约 79 个、`.log` 10 个、`.idea/` 20 个（全仓库共约 2041 个受控文件）。影响：重新克隆会下载大量无用文件，且随每次跑测试持续增长。建议后续单独处理（添加 `.gitignore` 并清理已跟踪的生成物）。

2. **`api/requirements.txt` 缺少 `openpyxl`**：`api/test_cases/test_excel_drive.py` 通过 `common/data_reader.py` 的 `read_excel()` 读取 `.xlsx`，缺少该库会直接报错，安装时需手动补装。

3. **Allure 依赖版本不统一**：`api` 使用 `allure-pytest==2.13.5`，`web_ui` 使用 `allure-pytest==2.16.0`。两者报告数据互相独立，不影响各自运行，但排查报告生成问题时需注意版本差异。

4. **`web_ui` 声明了 `python-dotenv` 但仓库中没有 `.env` 文件**：当前所有配置均走默认值或 `env_config.yaml`，不影响运行；若后续引入 `.env`，需自行创建且不应提交到仓库。

5. **`api/.venv` 使用 Python 3.14.0，另外两个模块使用 3.13.12**：重建环境时建议统一为 3.13.12，减少依赖兼容风险。

6. **虚拟环境不纳入版本控制**：三个 `venv` 目录均不会随仓库下载（这是正确做法），因此**每次重新克隆都必须执行第四节的步骤 1~3 重建环境**。

---

## 十、部署自检清单

克隆代码后，按顺序勾选以下每一项，全部通过即表示环境可正常使用：

- [ ] 已克隆仓库，且 `mall-lite/data/` 下有 6 个 JSON 文件
- [ ] `mall-lite/venv/` 已创建，`pip install -r requirements.txt` 成功
- [ ] `api/.venv/` 已创建，依赖安装成功（含手动补装的 `openpyxl`）
- [ ] `web_ui/venv/` 已创建，依赖安装成功
- [ ] `python -m playwright install chromium` 已执行成功
- [ ] `allure --version` 与 `java -version` 均能正常输出版本
- [ ] 在 `mall-lite` 目录执行 `python run.py`，终端显示启动成功
- [ ] `curl.exe http://localhost:8000/api/products` 返回含 `code` 的 JSON
- [ ] `api` 目录下 `pytest -m "smoke or p0"` 全部通过
- [ ] `web_ui` 目录下 `python run.py smoke` 全部通过
- [ ] `allure serve allure-results` 能正常打开 API 测试报告
- [ ] `allure serve reports/allure-results` 能正常打开 Web UI 测试报告

---

## 附：常用命令速查

```powershell
# ===== 启动后端 =====
cd D:\Faye\project\autotestskill\mall-lite
.\venv\Scripts\Activate.ps1
python run.py

# ===== API 测试 =====
cd D:\Faye\project\autotestskill\api
.\.venv\Scripts\Activate.ps1
pytest -m "smoke or p0"
pytest -m regression
allure serve allure-results

# ===== Web UI 测试 =====
cd D:\Faye\project\autotestskill\web_ui
.\venv\Scripts\Activate.ps1
python run.py smoke
python run.py all
python run.py report
```
