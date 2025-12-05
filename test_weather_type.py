import socketio
import time

# 创建SocketIO客户端
sio = socketio.Client()

# 连接事件
@sio.event
def connect():
    print('Connected to server')
    # 加入聊天室
    sio.emit('join', {'username': 'test_user'})
    time.sleep(1)
    # 发送天气查询
    sio.emit('send_message', {'message': '@天气 北京'})

# 新消息事件
@sio.event
def new_message(data):
    print('Received message:', data)
    # 检查是否包含weather_type
    if 'weather_type' in data:
        print('✓ Weather type found:', data['weather_type'])
    else:
        print('✗ Weather type not found in message')
    # 断开连接
    sio.disconnect()

# 运行测试
if __name__ == '__main__':
    try:
        sio.connect('http://localhost:5000')
        sio.wait()
    except Exception as e:
        print(f'Error: {e}')
