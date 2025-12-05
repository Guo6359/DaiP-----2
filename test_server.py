import sys
import os

print("Python版本:", sys.version)
print("当前目录:", os.getcwd())

# 尝试导入必要的模块
try:
    from flask import Flask
    print("Flask模块导入成功")
except ImportError as e:
    print("Flask模块导入失败:", e)

try:
    from flask_socketio import SocketIO
    print("Flask-SocketIO模块导入成功")
except ImportError as e:
    print("Flask-SocketIO模块导入失败:", e)

# 检查文件权限
try:
    with open('users.json', 'r') as f:
        print("users.json文件可以正常读取")
except Exception as e:
    print("读取users.json文件失败:", e)

try:
    with open('test_write.txt', 'w') as f:
        f.write("测试写入")
    os.remove('test_write.txt')
    print("文件写入权限正常")
except Exception as e:
    print("文件写入权限失败:", e)
