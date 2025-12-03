# AeroNetB Traceability API — 使用说明

本项目是一个基于 FastAPI + SQLAlchemy + SQLite 的供应链与质量可追溯系统原型，提供原材料追溯、批次关联、质量风险预警等模块，并带有基础的 JWT 认证与管理员权限控制。

## 目录
- 项目结构
- 环境与准备
- 安装依赖
- 启动服务
- 认证与权限
- 主要接口速览
- 示例请求（PowerShell）
- Web 页面
- 数据持久化
- 常见问题

## 项目结构
```
app.db                      # SQLite 数据库（运行后自动生成/使用）
db_clients.py               # 可选：数据库或客户相关辅助（若使用）
main.py                     # FastAPI 入口（路由、认证、CRUD）
models.py                   # SQLAlchemy 模型定义
requirements.txt            # Python 依赖清单
static/                     # 前端静态资源
templates/                  # Jinja2 模板（index.html 仪表盘）
Supply Chain and Quality Traceability Database Design Specification for AeroNetB Aerospace.md
```

## 环境与准备
- 操作系统：Windows（PowerShell）
- Python：建议 3.8+（项目 __pycache__ 显示曾使用 3.8）

## 安装依赖
在项目根目录（含 `requirements.txt` 的位置）执行：

```powershell
pip install -r requirements.txt
```

若您未安装 `pip` 或权限不足，请以管理员 PowerShell 运行或安装最新 Python。

## 启动服务
本项目使用 Uvicorn 作为 ASGI 服务器。启动后会自动创建/迁移表，并在数据库中植入一个管理员用户：
- 管理员账户：`admin`
- 初始密码：`admin123`

启动命令：
```powershell
.\.venv\Scripts\Activate.ps1; uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
访问：
- API 根：`http://localhost:8000/`
- 仪表盘：`http://localhost:8000/dashboard`
- OpenAPI/Swagger：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

## 认证与权限
本项目使用 JWT Bearer 认证：
- 登录接口：`POST /auth/login`（使用 OAuth2PasswordRequestForm 兼容表单字段）
- 成功登录后返回 `access_token`，在后续请求头中以 `Authorization: Bearer <token>` 携带
- 管理员专用接口需要管理员角色（`require_admin`），默认仅 `admin` 账户具备

安全参数（位于 `main.py` 顶部）：
- `SECRET_KEY`：默认占位，请在生产环境改为强随机值
- `ACCESS_TOKEN_EXPIRE_MINUTES`：令牌有效期（默认 8 小时）

## 主要接口速览
以下为核心模块的 CRUD 概览（具体字段见 `main.py` 中 Pydantic schema 与 `models.py` 中 SQLAlchemy 模型）：

- 原材料追溯 RawMaterialTraceRecord
  - `POST /raw-material-trace`（管理员）创建
  - `GET /raw-material-trace` 列表
  - `GET /raw-material-trace/{traceid}` 查询单条
  - `DELETE /raw-material-trace/{traceid}`（管理员）删除

- 批次追溯关联 BatchTraceRelation
  - `POST /batch-trace-relations`（管理员）创建
  - `GET /batch-trace-relations` 列表
  - `GET /batch-trace-relations/{relationid}` 查询单条
  - `DELETE /batch-trace-relations/{relationid}`（管理员）删除

- 质量风险预警 QualityRiskWarning
  - `POST /quality-risk-warnings`（管理员）创建
  - `GET /quality-risk-warnings` 列表
  - `GET /quality-risk-warnings/{warningid}` 查询单条
  - `DELETE /quality-risk-warnings/{warningid}`（管理员）删除

## 示例请求（PowerShell）
以下示例展示登录并访问需要认证的接口：

1) 登录获取 token
```powershell
$resp = Invoke-RestMethod -Method Post -Uri http://localhost:8000/auth/login -Body @{username='admin'; password='admin123'} -ContentType 'application/x-www-form-urlencoded'
$token = $resp.access_token
$headers = @{ Authorization = "Bearer $token" }
```

2) 创建原材料追溯记录（管理员）
```powershell
$body = @{
  traceid='T20241203001'
  materialbatchno='MBN-001'
  tracecode='TRC-RAW-001'
  supplierid='SUP-01'
  purchaseorderid='PO-2024-001'
  incominginspectionid='IQC-0001'
  storagelocation='WH-A-01'
  usedrecords=@()
  remainingqty=100.5
  tracestatus='In Stock'
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/raw-material-trace -Headers $headers -Body $body -ContentType 'application/json'
```

3) 列表查询
```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:8000/raw-material-trace -Headers $headers
```

4) 删除记录（管理员）
```powershell
Invoke-RestMethod -Method Delete -Uri http://localhost:8000/raw-material-trace/T20241203001 -Headers $headers
```

同理可对 `batch-trace-relations` 与 `quality-risk-warnings` 执行 CRUD 操作。注意：
- 创建批次关联时，`materialtracecode` 必须存在于原材料追溯记录中（由服务端校验）。

## Web 页面
- 仪表盘：`/dashboard` 使用 `templates/index.html` 与 `static/styles.css` 渲染。当前主要用于占位与可视化入口。

## 数据持久化
- 默认数据库：`sqlite:///./app.db`
- 首次启动将自动创建表，并植入管理员账户（如不存在）
- 若需要迁移到其他数据库，请修改 `main.py` 中 `SQLALCHEMY_DATABASE_URL` 以及 `create_engine` 参数

## 常见问题（FAQ）
- 登录返回 401：确认用户名/密码；默认管理员为 `admin/admin123`
- 调用管理员接口返回 403：确认请求头中带有 `Authorization: Bearer <token>` 且用户角色为 `admin`
- 令牌无效或过期：重新调用 `/auth/login` 获取新 token；检查系统时间与 `ACCESS_TOKEN_EXPIRE_MINUTES`
- 启动报错缺少模块：确保已激活虚拟环境并安装了 `requirements.txt`

## 开发/测试建议
- 通过 `http://localhost:8000/docs` 使用内置 Swagger 调试所有接口
- 使用仓库中的 `test_main.http` 在 IDE 中快速发起请求（记得先登录并替换 Bearer token）
- 对生产环境务必更换 `SECRET_KEY`，并启用 HTTPS、完善用户体系、审计与日志

---
如需扩展功能（分页查询、复杂筛选、批量导入、审计日志、操作记录、权限细粒度控制等），可以在 `models.py` 与 `main.py` 中新增字段与路由，并补充前端展示。
