# 创建必要的目录结构
import os

directories = [
    'core',
    'data',
    'logs',
    'static',
    'templates',
    'tests',
    'utils',
    'strategies',
    'notebooks'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    # 创建 __init__.py 文件
    init_file = os.path.join(directory, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f'"""\n{directory} 模块\n"""\n')

print("项目目录结构创建完成！")