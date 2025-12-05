import requests
import json

# 测试注册功能
def test_register():
    print("测试注册功能...")
    url = "http://localhost:5000/register"
    
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

# 测试登录功能
def test_login():
    print("\n测试登录功能...")
    url = "http://localhost:5000/login"
    
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
                print("登录成功！")
                return True
            else:
                print(f"登录失败: {data.get('error')}")
                return False
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # 测试注册
    register_success = test_register()
    
    # 测试登录
    if register_success:
        login_success = test_login()
    else:
        login_success = False
        
    print("\n测试完成！")
