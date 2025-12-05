import requests
import json

def test_weather_function():
    """测试@天气功能"""
    base_url = 'http://127.0.0.1:5000'
    
    # 创建一个会话来保持登录状态
    session = requests.Session()
    
    # 1. 注册一个新用户（如果用户已存在，会失败但不影响测试）
    register_data = {
        'username': 'test_weather_user',
        'password': 'test_password'
    }
    response = session.post(f'{base_url}/register', data=register_data)
    print(f"注册结果: {response.text}")
    
    # 2. 登录
    login_data = {
        'username': 'test_weather_user',
        'password': 'test_password'
    }
    response = session.post(f'{base_url}/login', data=login_data, allow_redirects=False)
    print(f"登录结果: {response.status_code}")
    
    # 3. 访问聊天页面，获取sessionid
    response = session.get(f'{base_url}/chat')
    print(f"访问聊天页面结果: {response.status_code}")
    
    # 4. 发送@天气 北京消息
    # 注意：这里我们模拟Socket.IO消息发送，实际上Socket.IO使用的是WebSocket协议
    # 为了简化测试，我们直接测试天气API调用部分
    city_name = '北京'
    weather_api_url = f'http://wthrcdn.etouch.cn/weather_mini?city={city_name}'
    response = requests.get(weather_api_url, timeout=5)
    response.encoding = 'utf-8'
    
    if response.status_code == 200:
        weather_data = response.json()
        print(f"天气API返回结果: {json.dumps(weather_data, ensure_ascii=False, indent=2)}")
        
        if weather_data['status'] == 1:
            print(f"天气查询成功！")
            print(f"城市: {weather_data['data']['city']}")
            print(f"温度: {weather_data['data']['wendu']}℃")
            print(f"天气: {weather_data['data']['forecast'][0]['type']}")
            print(f"风力: {weather_data['data']['forecast'][0]['fengxiang']}{weather_data['data']['fengli']}")
            print(f"湿度: {weather_data['data']['shidu']}")
            print(f"高低温: {weather_data['data']['forecast'][0]['low']} / {weather_data['data']['forecast'][0]['high']}")
        else:
            print(f"天气查询失败: {weather_data}")
    else:
        print(f"天气API调用失败: {response.status_code}")

if __name__ == '__main__':
    test_weather_function()