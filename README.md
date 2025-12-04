# AeroNetB Aerospace 数据库应用

本项目是一个使用 FastAPI + SQLAlchemy + SQLite 的示例应用，包含基础的认证、客户管理、生产订单、组件-零件关系等接口，并提供网页仪表盘页面。支持打包为单文件 EXE 便于分发。

## 环境要求
- Windows 10/11
- Python 3.10+（建议 3.10/3.11）

## 1. 开发运行（源代码）
1) 安装依赖：
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
2) 启动服务：
```
python main.py
```
3) 打开浏览器访问：
- 仪表盘页面：http://127.0.0.1:8000/dashboard
- 健康检查接口：http://127.0.0.1:8000/

初始会创建一个管理账号：
- 用户名：admin
- 密码：admin123

## 2. 接口简述
- POST /auth/login 使用用户名密码登录，返回 Bearer Token
- GET /me 使用 Authorization: Bearer <token> 获取当前用户信息
- 客户管理：
  - POST /clients 创建客户（管理员权限）
  - GET /clients 列出客户
  - GET /clients/{clientid} 获取客户
  - DELETE /clients/{clientid} 删除客户（管理员权限）
- 生产订单：
  - POST /production-orders 创建订单（管理员权限）
  - GET /production-orders 列出订单
  - GET /production-orders/{orderid} 获取订单
  - DELETE /production-orders/{orderid} 删除订单（管理员权限）
- 组件-零件关系：
  - POST /component-part-relations 创建关系（管理员权限）
  - GET /component-part-relations 列出关系
  - GET /component-part-relations/{relationid} 获取关系
  - DELETE /component-part-relations/{relationid} 删除关系（管理员权限）

示例：登录并调用受保护接口
```
POST http://127.0.0.1:8000/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```
将返回的 access_token 用作后续请求的 Authorization 头：
```
Authorization: Bearer <access_token>
```

## 3. 打包为 EXE
项目已提供打包脚本 `build_exe.py`，使用 PyInstaller 生成单文件 EXE，并复制 `static/` 与 `templates/` 到输出目录。

步骤：
1) 安装打包依赖（需要 pyinstaller）：
```
pip install -r requirements.txt
pip install pyinstaller
```
2) 运行打包脚本：
```
python build_exe.py
```
3) 完成后在 `dist/` 目录下会生成：
- `main.exe` 单文件可执行程序
- `static/` 与 `templates/` 资源目录

## 4. 运行 EXE
双击 `dist/main.exe` 或命令行运行：
```
.\u005Cdistmain.exe
```
默认监听 `127.0.0.1:8000`，使用方式与开发模式一致：访问 `/dashboard` 或调用各接口。

注意：首次运行会在程序根目录生成 SQLite 数据库文件 `app.db`。若使用 EXE，数据库位于与 EXE 同目录（工作目录）下。

## 5. 常见问题
- 端口占用：若 8000 端口被占用，请先关闭占用进程或修改 `main.py` 末尾的端口后再打包。
- 密钥：`SECRET_KEY` 为示例值，生产环境请替换为安全的随机字符串。
- 权限：部分接口需要管理员权限，请使用初始账号或自行创建管理员用户。

## 6. 结构
- `main.py` 启动 FastAPI 应用及路由
- `models.py` 通过 SQLAlchemy 定义数据表
- `templates/` Jinja2 模板（仪表盘页面）
- `static/` 静态资源（样式表等）
- `build_exe.py` 打包脚本
- `requirements.txt` 依赖列表

## 7. 许可证
示例项目，未设置许可证。若需分发，请添加适当许可证文件并遵守依赖的许可证条款。

