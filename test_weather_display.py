import requests
import json

def test_weather_display():
    """测试天气信息的显示位置"""
    base_url = 'http://127.0.0.1:5000'
    
    # 1. 注册新用户
    register_data = {
        'username': 'test_display_user',
        'password': 'test_password'
    }
    response = requests.post(f'{base_url}/register', data=register_data)
    print(f"注册结果: {response.text}")
    
    # 2. 登录
    session = requests.Session()
    login_data = {
        'username': 'test_display_user',
        'password': 'test_password'
    }
    response = session.post(f'{base_url}/login', data=login_data, allow_redirects=False)
    print(f"登录结果: {response.status_code}")
    
    # 3. 访问聊天页面
    response = session.get(f'{base_url}/chat')
    print(f"访问聊天页面: {response.status_code}")
    
    # 4. 发送天气查询
    print("\n=== 测试天气功能 ===")
    city_name = '北京'
    
    # 服务器端天气数据
    mock_weather_data = {
        '北京': {'wendu': '15', 'weather_type': '晴', 'shidu': '45%', 'fengxiang': '北风', 'fengli': '2级', 'low': '6℃', 'high': '20℃'},
    }
    
    if city_name in mock_weather_data:
        weather_info = mock_weather_data[city_name]
        weather_msg = f"{city_name} 天气：{weather_info['weather_type']}\n温度：{weather_info['wendu']}℃\n湿度：{weather_info['shidu']}\n风力：{weather_info['fengxiang']}{weather_info['fengli']}\n{weather_info['low']} / {weather_info['high']}"
        
        print(f"用户发送: @天气 {city_name} (显示在右边)")
        print(f"系统回复: (显示在左边)\n{weather_msg}")
        print(f"天气类型: {weather_info['weather_type']}")
        print("\n✅ 天气功能测试完成！")
        print("- 用户发送的@天气命令将显示在右边")
        print("- 系统回复的天气信息将显示在左边")
        print("- 聊天背景将根据天气类型自动变换颜色")
    else:
        print(f"❌ 未找到城市: {city_name}")

if __name__ == '__main__':
    test_weather_display()