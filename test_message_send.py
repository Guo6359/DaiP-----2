import requests
import time

# 测试登录
def test_login():
    print("\n=== 测试登录 ===")
    url = "http://localhost:5000/login"
    data = {
        "username": "111",
        "password": "123456"
    }
    response = requests.post(url, json=data)
    print(f"登录结果: {response.status_code}, {response.json()}")
    return response.json()

# 测试访问聊天页面
def test_chat_page(username):
    print("\n=== 测试访问聊天页面 ===")
    url = f"http://localhost:5000/chat?username={username}"
    response = requests.get(url)
    print(f"访问聊天页面: {response.status_code}")
    return response.status_code == 200

# 测试Socket.IO连接和消息发送
def test_socketio():
    print("\n=== 测试Socket.IO连接 ===")
    print("由于Socket.IO需要客户端库支持，建议手动测试以下功能：")
    print("1. 打开浏览器访问 http://localhost:5000")
    print("2. 注册/登录一个用户")
    print("3. 在聊天框中输入消息并发送")
    print("4. 检查消息是否正常显示在聊天框中")
    print("5. 测试@天气功能是否正常工作")

if __name__ == "__main__":
    # 测试登录
    login_result = test_login()
    if login_result.get("success"):
        username = login_result.get("username")
        # 测试访问聊天页面
        test_chat_page(username)
        
    # 提供手动测试指导
    test_socketio()