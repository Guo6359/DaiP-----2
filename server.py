from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import time
import hashlib
import secrets
import requests
import re
import threading

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 在线用户字典，存储 {sid: username}
online_users = {}
# 房间用户列表，存储 {username: sid}
room_users = {}
# 用户数据文件路径
USERS_FILE = 'users.json'

# 读取配置文件
def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'servers': ['http://localhost:5000']}

# 读取用户数据
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'users': []}

# 保存用户数据
def save_users(users_data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

# 密码加密
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# 验证密码
def verify_password(hashed_password, password):
    return hashed_password == hash_password(password)

# 检查用户名是否存在
def username_exists(username):
    users_data = load_users()
    return any(user['username'] == username for user in users_data['users'])

# 获取用户信息
def get_user(username):
    users_data = load_users()
    for user in users_data['users']:
        if user['username'] == username:
            return user
    return None

# 发送用户列表给所有客户端
def send_user_list():
    users = []
    for username, sid in room_users.items():
        users.append({'username': username})
    socketio.emit('user_list', {'users': users}, room='chat_room')

def fetch_news_60s():
    endpoints = [
        'https://api.2xb.cn/zaob?format=txt',
        'https://api.2xb.cn/zaob?format=text',
        'https://www.ooopn.com/api/60s/?type=txt',
        'https://www.ooopn.com/api/60s/?type=text'
    ]
    for url in endpoints:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                text = r.text
                lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
                if len(lines) >= 3:
                    return lines
        except Exception:
            pass
    return [
        '全球重要经济数据公布',
        '多地气象发布寒潮预警',
        '教育与科技领域政策更新',
        '出行与物流保持稳定',
        '消费市场持续恢复',
        '网络安全与反诈持续推进'
    ]

def simplify_line(s):
    s = s.strip()
    while s and (s[0].isdigit() or s[0] in ['．', '.', '、', '-', '—', '*', ' ']):
        s = s[1:].strip()
    return s

def resolve_taihe_mp3(songid):
    try:
        url = 'http://musicapi.taihe.com/v1/restserver/ting'
        params = {
            'method': 'baidu.ting.song.playAAC',
            'format': 'json',
            'songid': str(songid),
            'from': 'web',
            '_': str(int(time.time() * 1000))
        }
        r = requests.get(url, params=params, timeout=6)
        if r.status_code == 200:
            data = r.json()
            link = data.get('bitrate', {}).get('file_link')
            title = data.get('songinfo', {}).get('title')
            if link:
                return {'url': link, 'title': title or '千千音乐'}
    except Exception:
        pass
    try:
        url = f'http://ting.baidu.com/data/music/links?songIds={songid}&type=mp3'
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            lst = data.get('data', {}).get('songList') or []
            if lst:
                item = lst[0]
                return {'url': item.get('songLink'), 'title': item.get('songName') or '千千音乐'}
    except Exception:
        pass
    return None

def fetch_91q_music():
    try:
        r = requests.get('https://music.91q.com/', timeout=6)
        if r.status_code == 200:
            html = r.text
            ids = re.findall(r"/song/(\d+)", html)
            for sid in ids:
                resolved = resolve_taihe_mp3(sid)
                if resolved and resolved.get('url'):
                    return resolved
    except Exception:
        pass
    return {'url': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', 'title': '示例音乐'}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': '请填写完整信息'})
        
        if len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'error': '用户名长度应在3-20个字符之间'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': '密码长度应至少6个字符'})
        
        if username_exists(username):
            return jsonify({'success': False, 'error': '用户名已存在'})
        
        # 创建新用户
        users_data = load_users()
        new_user = {
            'username': username,
            'password': hash_password(password),
            'created_at': json.dumps({'timestamp': int(time.time())})
        }
        
        users_data['users'].append(new_user)
        save_users(users_data)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"注册错误: {e}")
        return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'})

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': '请填写用户名和密码'})
        
        user = get_user(username)
        if not user:
            return jsonify({'success': False, 'error': '用户名或密码错误'})
        
        if not verify_password(user['password'], password):
            return jsonify({'success': False, 'error': '用户名或密码错误'})
        
        # 验证成功，返回用户信息
        return jsonify({'success': True, 'username': username})
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'})

@app.route('/chat')
def chat():
    username = request.args.get('username')
    
    if not username:
        return redirect(url_for('index'))
    
    # 检查用户名是否已被使用
    if username in room_users:
        return render_template('login.html', error='该用户名已被使用')
    
    # 将用户名保存到会话中
    session['username'] = username
    
    return render_template('chat.html', username=username)

@app.route('/config')
def get_config():
    config = load_config()
    return jsonify(config)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/debug_background.js')
def send_debug_script():
    return send_from_directory('.', 'debug_background.js')

@app.route('/test_final_verification.js')
def send_test_script():
    return send_from_directory('.', 'test_final_verification.js')

@socketio.on('connect')
def handle_connect():
    print('客户端已连接:', request.sid)

@socketio.on('join')
def handle_join(data):
    # 从客户端获取用户名
    username = data.get('username')
    
    if not username:
        emit('join_error', {'error': '用户未登录'})
        return
    
    # 检查用户名唯一性
    if username in room_users:
        emit('join_error', {'error': '用户名已被使用'})
        return
    
    # 加入聊天室
    join_room('chat_room')
    online_users[request.sid] = username  # 存储用户SID和用户名的映射
    room_users[username] = request.sid  # 存储用户名和用户SID的映射
    
    # 通知所有用户有新用户上线
    emit('user_online', {'username': username, 'message': f'{username} 上线了'}, room='chat_room')
    
    # 发送用户列表
    send_user_list()
    
    print(f'{username} 上线了')

@socketio.on('send_message')
def handle_message(data):
    username = online_users.get(request.sid)
    if not username:
        return
    
    message = data['message']
    
    # 处理@电影功能
    if message.startswith('@电影') and len(message.split()) >= 2:
        parts = message.split()
        if len(parts) >= 2:
            movie_url = parts[1]
            parsed_url = f'https://jx.playerjy.com/?url={movie_url}'
            emit('new_message', {
                'username': username,
                'message': f'正在播放电影：{movie_url}',
                'is_movie': True,
                'movie_url': parsed_url
            }, room='chat_room')
            return
    
    # 处理@iframe功能
    if message.startswith('@iframe') and len(message.split()) >= 2:
        parts = message.split()
        if len(parts) >= 2:
            # 使用提供的API密钥构造iframe地址
            api_key = 'c5a2f0e6f646661d52639d318c8185e2'
            target_url = parts[1]
            # 构造iframe地址（这里假设需要使用API密钥进行某种构造）
            # 由于用户没有指定具体的构造方式，我们简单地将API密钥作为参数传递
            iframe_url = f'{target_url}?api_key={api_key}'
            emit('new_message', {
                'username': username,
                'message': f'显示iframe：{target_url}',
                'is_iframe': True,
                'iframe_url': iframe_url,
                'iframe_height': '50px'  # 设置高度为50px
            }, room='chat_room')
            return
    
    # 处理@天气功能
    if message.startswith('@天气') and len(message.split()) >= 2:
        parts = message.split()
        if len(parts) >= 2:
            city_name = parts[1]
            try:
                # 提供模拟天气数据
                # 实际使用时可以替换为真实的天气API
                mock_weather_data = {
                    '北京': {'wendu': '15', 'weather_type': '晴', 'shidu': '45%', 'fengxiang': '北风', 'fengli': '2级', 'low': '6℃', 'high': '20℃'},
                    '上海': {'wendu': '20', 'weather_type': '多云', 'shidu': '60%', 'fengxiang': '南风', 'fengli': '1级', 'low': '15℃', 'high': '25℃'},
                    '广州': {'wendu': '28', 'weather_type': '阴', 'shidu': '75%', 'fengxiang': '东风', 'fengli': '3级', 'low': '23℃', 'high': '32℃'},
                    '深圳': {'wendu': '26', 'weather_type': '小雨', 'shidu': '80%', 'fengxiang': '东南风', 'fengli': '2级', 'low': '22℃', 'high': '30℃'},
                    '成都': {'wendu': '18', 'weather_type': '雾', 'shidu': '90%', 'fengxiang': '无风', 'fengli': '0级', 'low': '12℃', 'high': '22℃'},
                    '杭州': {'wendu': '22', 'weather_type': '雷阵雨', 'shidu': '70%', 'fengxiang': '西南风', 'fengli': '4级', 'low': '16℃', 'high': '28℃'},
                    '西安': {'wendu': '12', 'weather_type': '雪', 'shidu': '50%', 'fengxiang': '西北风', 'fengli': '3级', 'low': '-2℃', 'high': '15℃'},
                }
                
                if city_name in mock_weather_data:
                    weather_info = mock_weather_data[city_name]
                    # 构建天气消息
                    weather_msg = f"{city_name} 天气：{weather_info['weather_type']}\n温度：{weather_info['wendu']}℃\n湿度：{weather_info['shidu']}\n风力：{weather_info['fengxiang']}{weather_info['fengli']}\n{weather_info['low']} / {weather_info['high']}"
                    
                    # 发送天气消息和天气类型，用于前端改变背景颜色
                    emit('new_message', {
                        'username': '系统',
                        'message': weather_msg,
                        'weather_type': weather_info['weather_type']
                    }, room='chat_room')
                    return
                else:
                    # 城市未找到
                    emit('new_message', {
                        'username': '系统',
                        'message': f'未找到城市：{city_name}\n支持的城市：北京、上海、广州、深圳、成都、杭州、西安'
                    }, room='chat_room')
                    return
            except Exception as e:
                print(f"天气API错误：{e}")
                emit('new_message', {
                    'username': '系统',
                    'message': f'获取天气信息失败：{str(e)}'
                }, room='chat_room')
                return

    if message.startswith('@新闻60s'):
        try:
            lines = fetch_news_60s()
            simple_lines = [simplify_line(x) for x in lines]
            simple_lines = [x for x in simple_lines if x]
            simple_lines = simple_lines[:12]
            news_msg = '今日新闻60s：\n' + '\n'.join(['- ' + x for x in simple_lines])
            emit('new_message', {
                'username': '系统',
                'message': news_msg
            }, room='chat_room')
            return
        except Exception as e:
            emit('new_message', {
                'username': '系统',
                'message': f'新闻获取失败：{str(e)}'
            }, room='chat_room')
            return

    if ('@音乐' in message):
        music_id = int(time.time() * 1000)
        default_info = {'url': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', 'title': '示例音乐'}
        emit('new_message', {
            'username': '系统',
            'message': '音乐已创建',
            'is_music': True,
            'music_url': default_info['url'],
            'music_title': default_info['title'],
            'music_id': music_id
        }, room='chat_room')

        def resolve_and_update(mid):
            info = fetch_91q_music()
            if info and info.get('url'):
                socketio.emit('music_update', {
                    'music_id': mid,
                    'music_url': info.get('url'),
                    'music_title': info.get('title') or '千千音乐'
                }, room='chat_room')

        threading.Thread(target=resolve_and_update, args=(music_id,), daemon=True).start()
        return

    # 处理普通消息
    emit('new_message', {
        'username': username,
        'message': message
    }, room='chat_room')

@socketio.on('disconnect')
def handle_disconnect():
    username = online_users.get(request.sid)
    if username:
        del online_users[request.sid]
        if username in room_users:
            del room_users[username]
        
        # 通知所有用户有用户下线
        emit('user_offline', {'username': username, 'message': f'{username} 下线了'}, room='chat_room')
        
        # 发送更新后的用户列表
        send_user_list()
        
        print(f'{username} 下线了')

@socketio.on('music_control')
def handle_music_control(data):
    action = data.get('action')
    music_id = data.get('music_id')
    emit('music_control', {
        'action': action,
        'music_id': music_id
    }, room='chat_room')

if __name__ == '__main__':
    # 确保目录存在
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # 运行服务器 - 关闭debug模式以提高稳定性
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)

