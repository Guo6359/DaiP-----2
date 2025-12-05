import socketio
import time
import json
import threading
import random

# 创建Socket.IO客户端
sio = socketio.Client()

# 测试状态
is_testing = True
message_count = 0
received_count = 0
send_errors = 0
connection_lost = False

def print_with_timestamp(message):
    """带时间戳的打印函数"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

# 事件处理函数
@sio.on('connect')
def on_connect():
    print_with_timestamp('✓ 已连接到服务器')
    
    # 发送join事件
    try:
        sio.emit('join', {'username': 'browser_test_user'})
    except Exception as e:
        print_with_timestamp(f'❌ 发送join事件失败: {e}')

@sio.on('new_message')
def on_new_message(data):
    global received_count, is_testing
    print_with_timestamp(f'收到消息 #{received_count + 1}: {json.dumps(data, ensure_ascii=False)}')
    received_count += 1
    
    # 如果收到了所有预期的消息，结束测试
    if received_count >= 3 and is_testing:
        print_with_timestamp('✓ 测试完成')
        is_testing = False
        sio.disconnect()

@sio.on('user_online')
def on_user_online(data):
    print_with_timestamp(f'✓ 用户状态更新: {data["message"]}')
    
    # 模拟浏览器中的连续消息发送场景
    def simulate_browser_interaction():
        global message_count, send_errors, connection_lost
        
        # 等待一小段时间，模拟用户阅读欢迎信息
        time.sleep(2)
        
        # 发送第一条天气查询
        try:
            message_count += 1
            weather_msg1 = '@天气 北京'
            print_with_timestamp(f'发送天气查询 #{message_count}: {weather_msg1}')
            sio.emit('send_message', {'message': weather_msg1})
        except Exception as e:
            print_with_timestamp(f'❌ 发送消息 #{message_count}失败: {e}')
            send_errors += 1
        
        # 模拟用户快速连续发送第二条消息
        try:
            time.sleep(0.5)  # 模拟用户快速连续输入
            message_count += 1
            weather_msg2 = '@天气 上海'
            print_with_timestamp(f'发送天气查询 #{message_count}: {weather_msg2}')
            sio.emit('send_message', {'message': weather_msg2})
        except Exception as e:
            print_with_timestamp(f'❌ 发送消息 #{message_count}失败: {e}')
            send_errors += 1
        
        # 模拟用户稍等后发送第三条消息
        try:
            time.sleep(1)  # 模拟用户稍作思考后输入
            message_count += 1
            weather_msg3 = '@天气 广州'
            print_with_timestamp(f'发送天气查询 #{message_count}: {weather_msg3}')
            sio.emit('send_message', {'message': weather_msg3})
        except Exception as e:
            print_with_timestamp(f'❌ 发送消息 #{message_count}失败: {e}')
            send_errors += 1
    
    # 在新线程中执行，模拟浏览器的异步行为
    threading.Thread(target=simulate_browser_interaction, daemon=True).start()

@sio.on('disconnect')
def on_disconnect():
    global connection_lost
    print_with_timestamp('✓ 与服务器断开连接')
    connection_lost = True

@sio.on('connect_error')
def on_connect_error(data):
    print_with_timestamp(f'❌ 连接错误: {data}')

@sio.on('reconnect')
def on_reconnect():
    print_with_timestamp('✓ 重新连接到服务器')

# 定期检查连接状态
def check_connection_status():
    global is_testing, connection_lost
    while is_testing:
        if not sio.connected:
            connection_lost = True
            print_with_timestamp('⚠️ 检测到连接断开')
        time.sleep(1)

# 运行测试
try:
    print_with_timestamp('开始模拟浏览器场景测试...')
    
    # 连接到服务器
    sio.connect('http://localhost:5000', transports=['websocket'])
    
    # 启动连接状态检查线程
    threading.Thread(target=check_connection_status, daemon=True).start()
    
    # 设置超时时间为15秒
    timeout = time.time() + 15
    while is_testing and time.time() < timeout:
        time.sleep(0.1)
    
    if is_testing:
        print_with_timestamp('❌ 测试超时: 没有在规定时间内收到所有响应')
        sio.disconnect()
        
except Exception as e:
    print_with_timestamp(f'❌ 测试过程中发生异常: {e}')

finally:
    # 打印测试结果
    print_with_timestamp('\n=== 浏览器场景模拟测试结果 ===')
    print_with_timestamp(f'发送消息数量: {message_count}')
    print_with_timestamp(f'接收消息数量: {received_count}')
    print_with_timestamp(f'发送错误数量: {send_errors}')
    print_with_timestamp(f'连接是否断开: {connection_lost}')
    
    if received_count >= message_count - send_errors:
        print_with_timestamp('✅ 测试通过: 所有消息都得到了响应')
    else:
        print_with_timestamp('❌ 测试失败: 部分消息没有得到响应')
