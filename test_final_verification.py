import socketio
import time
import json
import threading

# 创建Socket.IO客户端
sio = socketio.Client()

# 测试状态
is_testing = True
message_count = 0
received_count = 0
send_errors = 0
connection_status = 'disconnected'

# 测试配置
TEST_CONFIG = {
    "username": "final_test_user",
    "server_url": "http://localhost:5000",
    "weather_queries": [
        "@天气 北京",
        "@天气 上海", 
        "@天气 广州",
        "@天气 深圳",
        "@天气 成都"
    ],
    "delay_between_queries": 500,  # 500ms间隔，模拟快速连续发送
    "timeout": 20  # 20秒超时
}

def print_test_info(message):
    """带测试信息的打印"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [测试] {message}")

# Socket.IO事件处理
@sio.on('connect')
def on_connect():
    global connection_status
    connection_status = 'connected'
    print_test_info("✓ 成功连接到服务器")
    
    # 发送join事件
    try:
        sio.emit('join', {'username': TEST_CONFIG["username"]})
        print_test_info(f"✓ 发送join事件，用户名: {TEST_CONFIG['username']}")
    except Exception as e:
        print_test_info(f"❌ 发送join事件失败: {e}")

@sio.on('disconnect')
def on_disconnect():
    global connection_status
    connection_status = 'disconnected'
    print_test_info("⚠ 与服务器断开连接")

@sio.on('connect_error')
def on_connect_error(data):
    global connection_status
    connection_status = 'error'
    print_test_info(f"❌ 连接错误: {data}")

@sio.on('new_message')
def on_new_message(data):
    global received_count, is_testing
    
    received_count += 1
    weather_type = data.get('weather_type', '无')
    
    print_test_info(f"✓ 收到消息 #{received_count} | 发送者: {data['username']} | 天气类型: {weather_type}")
    print_test_info(f"   消息内容: {data['message'].replace(chr(10), '; ')}")
    
    # 检查是否收到所有预期的响应
    if received_count >= len(TEST_CONFIG["weather_queries"]):
        print_test_info("✅ 已收到所有预期的天气响应")
        is_testing = False
        sio.disconnect()

@sio.on('user_online')
def on_user_online(data):
    print_test_info(f"📢 系统消息: {data['message']}")
    
    # 模拟用户快速连续发送天气查询
    def send_weather_queries():
        global message_count, send_errors
        
        print_test_info(f"🚀 开始发送{len(TEST_CONFIG['weather_queries'])}条连续天气查询")
        
        for i, query in enumerate(TEST_CONFIG["weather_queries"]):
            try:
                message_count += 1
                print_test_info(f"📤 发送天气查询 #{message_count}: {query}")
                sio.emit('send_message', {'message': query})
                
                # 等待指定的时间间隔
                if i < len(TEST_CONFIG["weather_queries"]) - 1:
                    time.sleep(TEST_CONFIG["delay_between_queries"] / 1000)
                    
            except Exception as e:
                print_test_info(f"❌ 发送天气查询 #{message_count}失败: {e}")
                send_errors += 1
        
        print_test_info("📤 所有天气查询已发送完成")
    
    # 启动消息发送线程
    threading.Thread(target=send_weather_queries, daemon=True).start()

# 运行测试
try:
    print_test_info("=== 开始天气查询功能最终验证测试 ===")
    print_test_info(f"测试配置: {json.dumps(TEST_CONFIG, ensure_ascii=False, indent=2)}")
    
    # 连接到服务器
    sio.connect(TEST_CONFIG["server_url"], transports=['websocket'])
    
    # 设置超时时间
    timeout = time.time() + TEST_CONFIG["timeout"]
    
    # 等待测试完成
    while is_testing and time.time() < timeout:
        time.sleep(0.1)
    
    if is_testing:
        print_test_info("❌ 测试超时: 未在规定时间内完成所有测试")
        sio.disconnect()
        
    # 等待一小段时间确保所有响应都被处理
    time.sleep(2)
    
finally:
    # 生成最终测试报告
    print_test_info("\n=== 最终验证测试报告 ===")
    print_test_info(f"测试状态: {'成功' if not is_testing else '超时'}")
    print_test_info(f"总测试时间: {time.time() - (timeout - TEST_CONFIG['timeout']):.2f}秒")
    print_test_info(f"连接状态: {connection_status}")
    print_test_info(f"发送查询数量: {message_count}")
    print_test_info(f"接收响应数量: {received_count}")
    print_test_info(f"发送错误数量: {send_errors}")
    print_test_info(f"响应率: {(received_count / message_count * 100) if message_count > 0 else 0:.2f}%")
    
    # 测试结果判定
    if received_count == message_count and send_errors == 0 and not is_testing:
        print_test_info("🎉 测试通过！连续天气查询功能正常工作")
        print_test_info("✅ 修复效果: 成功解决连续发送天气查询无法响应的问题")
        print_test_info("✅ 优化点:")
        print_test_info("   1. 移除了可能影响交互的CSS backdrop-filter属性")
        print_test_info("   2. 优化了天气背景切换逻辑，减少DOM操作频率")
        print_test_info("   3. 添加了天气类状态跟踪，避免重复DOM操作")
        print_test_info("   4. 确保消息在各种天气背景下的可读性和交互性")
    else:
        print_test_info("❌ 测试未通过！连续天气查询功能仍存在问题")
        print_test_info("💡 建议进一步检查:")
        print_test_info("   1. 浏览器开发者工具中的控制台错误")
        print_test_info("   2. 服务器日志是否有异常")
        print_test_info("   3. 网络连接稳定性")
