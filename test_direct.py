import requests
import json
import threading
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入服务器模块
import server

# 启动服务器的函数
def start_server():
    print("启动服务器...")
    server.socketio.run(server.app, host='0.0.0.0', port=8000, debug=False, use_reloader=False)

# 测试注册功能
def test_register():
    print("等待服务器启动...")
    time.sleep(2)  # 等待服务器启动
    
    print("测试注册功能...")
    url = "http://localhost:8000/register"
    
    # 测试数据
    test_data = {
        "username": "test_user",
        "password": "test_password"
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=test_data)
        
        # 打印响应
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("注册成功！")
                return True
            else:
                print(f"注册失败: {data.get('error')}")
                return False
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # 创建服务器线程
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True  # 守护线程，主线程结束后自动退出
    
    # 启动服务器
    server_thread.start()
    
    # 测试注册功能
    test_register()
    
    # 等待一段时间后退出
    time.sleep(1)
    print("测试完成！")
