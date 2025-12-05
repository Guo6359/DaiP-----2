import requests
import socketio
import time
import json

# 创建Socket.IO客户端
sio = socketio.Client()

# 测试状态
is_testing = True
message_count = 0
received_count = 0

# 事件处理函数
@sio.on('connect')
def on_connect():
    print('✓ 已连接到服务器')
    # 发送join事件
    sio.emit('join', {'username': 'test_weather_user'})

@sio.on('new_message')
def on_new_message(data):
    global received_count, is_testing
    print(f'收到消息 #{received_count + 1}: {json.dumps(data, ensure_ascii=False)}')
    received_count += 1
    
    # 如果收到了所有预期的消息，结束测试
    if received_count >= 2 and is_testing:
        print('✓ 测试完成')
        is_testing = False
        sio.disconnect()

@sio.on('user_online')
def on_user_online(data):
    print(f'✓ 用户状态更新: {data["message"]}')
    
    # 连续发送两条天气查询消息
    def send_multiple_weather_queries():
        global message_count
        
        # 第一条天气查询
        message_count += 1
        weather_msg1 = '@天气 北京'
        print(f'发送天气查询 #{message_count}: {weather_msg1}')
        sio.emit('send_message', {'message': weather_msg1})
        
        # 第二条天气查询（快速连续发送）
        message_count += 1
        weather_msg2 = '@天气 上海'
        print(f'发送天气查询 #{message_count}: {weather_msg2}')
        sio.emit('send_message', {'message': weather_msg2})
    
    # 使用定时器确保用户已加入房间
    time.sleep(1)
    send_multiple_weather_queries()

@sio.on('disconnect')
def on_disconnect():
    print('✓ 与服务器断开连接')
    
    # 打印测试结果
    print(f'\n=== 连续天气查询测试结果 ===')
    print(f'发送消息数量: {message_count}')
    print(f'接收消息数量: {received_count}')
    
    if received_count == message_count:
        print('✅ 测试通过: 所有消息都得到了响应')
    else:
        print('❌ 测试失败: 部分消息没有得到响应')

# 运行测试
try:
    print('连接到服务器...')
    sio.connect('http://localhost:5000')
    
    # 设置超时时间为10秒
    timeout = time.time() + 10
    while is_testing and time.time() < timeout:
        time.sleep(0.1)
    
    if is_testing:
        print('❌ 测试超时: 没有在规定时间内收到所有响应')
        sio.disconnect()
        print(f'\n=== 连续天气查询测试结果 ===')
        print(f'发送消息数量: {message_count}')
        print(f'接收消息数量: {received_count}')
        print('❌ 测试失败: 部分消息没有得到响应')
except Exception as e:
    print(f'❌ 测试失败: {e}')
