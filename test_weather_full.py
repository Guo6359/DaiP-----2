import requests
import socketio
import time
import json

# 创建Socket.IO客户端
sio = socketio.Client()

# 测试结果
weather_test_result = {
    "connected": False,
    "joined": False,
    "sent_weather_request": False,
    "received_weather_response": False,
    "weather_data_correct": False,
    "weather_type_present": False
}

# 事件处理函数
@sio.on('connect')
def on_connect():
    print('✓ 已连接到服务器')
    weather_test_result["connected"] = True
    # 发送join事件
    sio.emit('join', {'username': 'test_weather_user'})

@sio.on('new_message')
def on_new_message(data):
    print(f'收到消息: {json.dumps(data, ensure_ascii=False)}')
    
    # 如果是天气消息，检查是否正确
    if data['username'] == '系统' and '天气' in data['message']:
        print('✓ 收到天气信息')
        weather_test_result["received_weather_response"] = True
        
        # 检查天气数据是否包含正确信息
        if '温度' in data['message'] and '湿度' in data['message'] and '风力' in data['message']:
            print('✓ 天气数据格式正确')
            weather_test_result["weather_data_correct"] = True
        
        # 检查是否包含weather_type字段
        if 'weather_type' in data:
            print(f'✓ 包含天气类型: {data["weather_type"]}')
            weather_test_result["weather_type_present"] = True
        
        # 断开连接并打印测试结果
        sio.disconnect()

@sio.on('user_online')
def on_user_online(data):
    print(f'✓ 用户状态更新: {data["message"]}')
    weather_test_result["joined"] = True
    
    # 发送天气查询 - 测试多个城市
    cities = ['北京', '上海', '广州', '深圳', '成都', '杭州', '西安']
    
    def send_weather_queries():
        for city in cities:
            time.sleep(0.5)  # 等待0.5秒
            weather_msg = f'@天气 {city}'
            print(f'发送天气查询: {weather_msg}')
            weather_test_result["sent_weather_request"] = True
            sio.emit('send_message', {'message': weather_msg})
            # 只测试一个城市就可以了
            break
    
    # 使用定时器确保用户已加入房间
    time.sleep(1)
    send_weather_queries()

@sio.on('disconnect')
def on_disconnect():
    print('✓ 与服务器断开连接')
    
    # 打印完整测试结果
    print('\n=== 天气功能测试结果 ===')
    for test_name, result in weather_test_result.items():
        status = "通过" if result else "失败"
        print(f'{test_name}: {status}')
    
    # 总结
    all_tests_passed = all(weather_test_result.values())
    print(f'\n整体测试结果: {"全部通过" if all_tests_passed else "部分失败"}')

# 运行测试
try:
    print('连接到服务器...')
    sio.connect('http://localhost:5000')
    sio.wait()
except Exception as e:
    print(f'测试失败: {e}')
    for test_name in weather_test_result:
        weather_test_result[test_name] = False
    
    # 打印测试结果
    print('\n=== 天气功能测试结果 ===')
    for test_name, result in weather_test_result.items():
        status = "通过" if result else "失败"
        print(f'{test_name}: {status}')
