import sys
import os
import shutil

# 获取当前脚本所在目录
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, 'static')
templates_dir = os.path.join(base_dir, 'templates')
dist_dir = os.path.join(base_dir, 'dist')

# 打包 main.py 为单文件 exe，包含静态文件和模板，并处理 passlib 的依赖
cmd = (
    'pyinstaller --onefile '
    '--add-data "static;static" '
    '--add-data "templates;templates" '
    '--hidden-import=passlib.handlers.pbkdf2 '
    'main.py --clean'
)

print('执行命令:')
print(cmd)
os.system(cmd)

# 复制 static 和 templates 到 dist 目录，防止 exe 运行时找不到目录
if os.path.exists(dist_dir):
    if os.path.exists(static_dir):
        shutil.copytree(static_dir, os.path.join(dist_dir, 'static'), dirs_exist_ok=True)
    if os.path.exists(templates_dir):
        shutil.copytree(templates_dir, os.path.join(dist_dir, 'templates'), dirs_exist_ok=True)
print('static 和 templates 目录已复制到 dist 目录。')
