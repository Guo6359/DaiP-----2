import requests
import socketio
import time

# 创建Socket.IO客户端
sio = socketio.Client()

# 事件处理函数
@sio.on('connect')
def on_connect():
    print('已连接到服务器')
    # 发送join事件
    sio.emit('join', {'username': 'test_weather_user'})

@sio.on('new_message')
def on_new_message(data):
    print(f'收到消息: {data}')
    
    # 如果是天气消息，检查是否正确
    if data['username'] == '系统' and '天气' in data['message']:
        print('天气功能测试成功!')
        sio.disconnect()

@sio.on('user_online')
def on_user_online(data):
    print(f'用户状态: {data}')
    # 发送天气查询
    time.sleep(1)  # 等待1秒确保用户已加入房间
    print('发送天气查询: @天气 北京')
    sio.emit('send_message', {'message': '@天气 北京'})

@sio.on('disconnect')
def on_disconnect():
    print('与服务器断开连接')

# 运行测试
try:
    print('连接到服务器...')
    sio.connect('http://localhost:5000')
    sio.wait()
except Exception as e:
    print(f'测试失败: {e}')
