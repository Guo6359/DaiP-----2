document.addEventListener('DOMContentLoaded', function() {
    // 获取URL中的用户名参数
    const urlParams = new URLSearchParams(window.location.search);
    const username = urlParams.get('username');
    
    if (!username) {
        // 如果没有用户名，重定向到登录页面
        window.location.href = '/';
        return;
    }

    // 存储当前用户信息
    let currentUser = {
        username: username,
        id: null
    };

    // 获取DOM元素
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const usersContainer = document.getElementById('users-container');
    const userCount = document.getElementById('user-count');
    
    // 常用表情列表
    const commonEmojis = [
        '😊', '😂', '😍', '🥰', '🤔', '😮', '😎', '🥳',
        '👍', '👎', '❤️', '🎉', '🔥', '🙌', '👏', '😢',
        '😡', '😴', '🤗', '😇', '🤩', '😋', '🤗', '😘'
    ];
    
    // 创建表情选择器
    function createEmojiSelector() {
        const emojiContainer = document.createElement('div');
        emojiContainer.id = 'emoji-container';
        emojiContainer.className = 'emoji-container';
        emojiContainer.style.display = 'none';
        
        commonEmojis.forEach(emoji => {
            const emojiBtn = document.createElement('button');
            emojiBtn.className = 'emoji-btn';
            emojiBtn.textContent = emoji;
            emojiBtn.onclick = () => insertEmoji(emoji);
            emojiContainer.appendChild(emojiBtn);
        });
        
        return emojiContainer;
    }
    
    // 插入表情到输入框
    function insertEmoji(emoji) {
        const startPos = messageInput.selectionStart;
        const endPos = messageInput.selectionEnd;
        const currentValue = messageInput.value;
        
        messageInput.value = currentValue.substring(0, startPos) + emoji + currentValue.substring(endPos);
        messageInput.focus();
        
        // 设置光标位置
        const newPos = startPos + emoji.length;
        messageInput.setSelectionRange(newPos, newPos);
        
        // 调整输入框高度
        adjustTextareaHeight();
    }
    
    // 添加表情按钮和选择器
    const emojiBtn = document.createElement('button');
    emojiBtn.id = 'emoji-btn';
    emojiBtn.className = 'emoji-btn-toggle';
    emojiBtn.textContent = '😊';
    emojiBtn.onclick = () => {
        const emojiContainer = document.getElementById('emoji-container');
        emojiContainer.style.display = emojiContainer.style.display === 'none' ? 'block' : 'none';
    };
    
    // 添加音乐按钮
    const musicBtn = document.createElement('button');
    musicBtn.id = 'music-btn';
    musicBtn.className = 'emoji-btn-toggle';
    musicBtn.textContent = '🎵';
    musicBtn.title = '添加音乐';
    musicBtn.onclick = () => {
        // 直接发送@音乐命令
        socket.emit('send_message', { message: '@音乐' });
    };
    
    // 将表情按钮和音乐按钮添加到发送按钮前面
    sendBtn.parentNode.insertBefore(emojiBtn, sendBtn);
    sendBtn.parentNode.insertBefore(musicBtn, sendBtn);
    
    // 添加表情选择器到页面
    const emojiContainer = createEmojiSelector();
    document.body.appendChild(emojiContainer);
    
    // 点击页面其他地方关闭表情选择器
    document.addEventListener('click', function(e) {
        if (!emojiBtn.contains(e.target) && !emojiContainer.contains(e.target)) {
            emojiContainer.style.display = 'none';
        }
    });

    // 建立Socket.IO连接
    const socket = io();

    // 发送加入房间事件，包含用户名
    socket.emit('join', {username: username});

    // 处理加入房间错误
    socket.on('join_error', function(data) {
        showSystemMessage(data.error);
        // 延迟后返回登录页面
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    });
    
    // 处理用户上线通知
    socket.on('user_online', function(data) {
        showSystemMessage(`${data.username} 上线了`);
    });
    
    // 处理用户下线通知
    socket.on('user_offline', function(data) {
        showSystemMessage(`${data.username} 下线了`);
    });

    // 添加消息到聊天界面
    function addMessage(username, message, isSystem = false, isUser = false, isMovie = false, movieUrl = '', isIframe = false, iframeUrl = '', iframeHeight = '50px') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isSystem ? 'system' : (isUser ? 'user' : 'other')}`;
        
        if (!isSystem) {
            const headerDiv = document.createElement('div');
            headerDiv.className = 'message-header';
            headerDiv.textContent = username;
            messageDiv.appendChild(headerDiv);
        }
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        // 使用textContent来正确显示emoji
        contentDiv.textContent = message;
        messageDiv.appendChild(contentDiv);
        
        // 如果是电影消息，添加iframe
        if (isMovie && movieUrl) {
            const movieContainer = document.createElement('div');
            movieContainer.className = 'movie-container';
            const iframe = document.createElement('iframe');
            iframe.src = movieUrl;
            iframe.allowFullscreen = true;
            movieContainer.appendChild(iframe);
            messageDiv.appendChild(movieContainer);
        }
        
        // 如果是iframe消息，添加iframe
        if (isIframe && iframeUrl) {
            const iframeContainer = document.createElement('div');
            iframeContainer.className = 'iframe-container';
            const iframe = document.createElement('iframe');
            iframe.src = iframeUrl;
            iframe.style.height = iframeHeight || '50px';
            iframe.frameBorder = '0';
            iframe.allowFullscreen = true;
            iframeContainer.appendChild(iframe);
            messageDiv.appendChild(iframeContainer);
        }
        
        chatMessages.appendChild(messageDiv);
        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv;
    }

    // 显示系统消息
    function showSystemMessage(message) {
        addMessage('', message, true);
    }

    // 更新在线用户列表
    function updateUserList(users) {
        usersContainer.innerHTML = '';
        userCount.textContent = users.length;
        
        users.forEach(user => {
            const userItem = document.createElement('div');
            userItem.className = 'user-item';
            userItem.textContent = user.username;
            usersContainer.appendChild(userItem);
        });
    }

    // 发送消息
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;
        
        // 发送消息到服务器
        socket.emit('send_message', { message: message });
        
        // 清空输入框
        messageInput.value = '';
        // 调整输入框高度
        messageInput.style.height = 'auto';
    }

    // 退出聊天室
    function logout() {
        socket.disconnect();
        window.location.href = '/';
    }

    // 自动调整文本框高度
    function adjustTextareaHeight() {
        messageInput.style.height = 'auto';
        messageInput.style.height = (messageInput.scrollHeight) + 'px';
    }

    // 事件监听
    sendBtn.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keydown', function(e) {
        // 按Ctrl+Enter或Shift+Enter换行
        if ((e.ctrlKey || e.shiftKey) && e.key === 'Enter') {
            return;
        }
        // 按Enter发送消息
        if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    messageInput.addEventListener('input', adjustTextareaHeight);
    
    logoutBtn.addEventListener('click', logout);

    // Socket.IO事件监听
    socket.on('connect', function() {
        console.log('已连接到服务器');
    });

    socket.on('disconnect', function() {
        console.log('与服务器断开连接');
        showSystemMessage('与服务器断开连接');
    });

    socket.on('user_joined', function(data) {
        showSystemMessage(data.message);
    });

    socket.on('user_left', function(data) {
        showSystemMessage(data.message);
    });

    // 根据天气类型设置背景颜色 - 修复版本
    function setWeatherBackground(weatherType) {
        if (!weatherType) return;
        
        console.log('Setting weather background for:', weatherType);
        
        const body = document.body;
        let newClass = '';
        
        // 映射天气类型到对应的CSS类
        switch(weatherType) {
            case '晴':
                newClass = 'weather-sunny';
                break;
            case '多云':
            case '阴':
                newClass = 'weather-cloudy';
                break;
            case '小雨':
            case '中雨':
            case '大雨':
            case '暴雨':
            case '阵雨':
                newClass = 'weather-rainy';
                break;
            case '雪':
            case '小雪':
            case '中雪':
            case '大雪':
            case '暴雪':
                newClass = 'weather-snowy';
                break;
            case '雾':
            case '霾':
                newClass = 'weather-foggy';
                break;
            case '雷阵雨':
                newClass = 'weather-stormy';
                break;
            default:
                // 默认背景 - 不设置新类
                break;
        }
        
        console.log('New weather class:', newClass);
        
        // 移除所有天气相关类
        const weatherClasses = ['weather-sunny', 'weather-cloudy', 'weather-rainy', 'weather-snowy', 'weather-foggy', 'weather-stormy'];
        weatherClasses.forEach(cls => {
            body.classList.remove(cls);
        });
        
        // 添加新的天气背景类
        if (newClass) {
            body.classList.add(newClass);
            console.log('Added class:', newClass);
        }
        
        console.log('Final body classes:', body.className);
        console.log('天气背景已设置:', weatherType);
    }
    
    socket.on('new_message', function(data) {
        const isUser = data.username === username;
        const msgEl = addMessage(
            data.username, 
            data.message, 
            false, 
            isUser, 
            data.is_movie, 
            data.movie_url,
            data.is_iframe,
            data.iframe_url,
            data.iframe_height
        );
        
        // 如果消息包含天气类型，设置背景颜色
        console.log('Received message:', data);
        if (data.weather_type) {
            console.log('Setting weather background for type:', data.weather_type);
            setWeatherBackground(data.weather_type);
            console.log('Current body classes:', document.body.className);
        }
        console.log('Music check:', data.is_music, data.music_url, data.music_id);
        if (data.is_music && data.music_url && data.music_id) {
            console.log('Creating music card:', data.music_url, data.music_id, data.music_title);
            const card = createMusicCard(data.music_url, data.music_id, data.music_title);
            msgEl.appendChild(card);
        }
    });

    socket.on('music_control', function(data) {
        const audio = musicMap.get(data.music_id);
        if (!audio) return;
        if (data.action === 'play') {
            audio.play().catch(function(){});
        } else if (data.action === 'pause') {
            audio.pause();
        } else if (data.action === 'stop') {
            audio.pause();
            audio.currentTime = 0;
        }
    });

    socket.on('music_update', function(data) {
        const musicId = data.music_id;
        const musicUrl = data.music_url;
        const title = data.music_title;
        const audio = musicMap.get(musicId);
        if (!audio) return;
        if (musicUrl) {
            const wasPlaying = !audio.paused;
            audio.src = musicUrl;
            if (wasPlaying) {
                audio.play().catch(function(){});
            }
        }
        // 找到对应的音乐卡片
        const card = document.querySelector(`[data-music-id="${musicId}"]`);
        if (card) {
            // 更新音乐标题
            const titleEl = card.querySelector('.music-title');
            if (titleEl) {
                titleEl.textContent = title;
            }
        }
    });

    socket.on('user_list', function(data) {
        updateUserList(data.users);
    });

    // 音乐功能
    const musicMap = new Map();

    function createMusicCard(musicUrl, musicId, title) {
        const card = document.createElement('div');
        card.className = 'music-card';
        card.setAttribute('data-music-id', musicId);
        const header = document.createElement('div');
        header.className = 'music-title';
        header.textContent = title || '音乐';
        const controls = document.createElement('div');
        controls.className = 'music-controls';
        const btnPlay = document.createElement('button');
        btnPlay.className = 'music-btn';
        btnPlay.textContent = '播放';
        const btnPause = document.createElement('button');
        btnPause.className = 'music-btn';
        btnPause.textContent = '暂停';
        const btnStop = document.createElement('button');
        btnStop.className = 'music-btn stop';
        btnStop.textContent = '停止';
        const audio = document.createElement('audio');
        audio.src = musicUrl;
        audio.preload = 'auto';
        audio.style.display = 'none';
        musicMap.set(musicId, audio);
        btnPlay.onclick = function() { socket.emit('music_control', { action: 'play', music_id: musicId }); };
        btnPause.onclick = function() { socket.emit('music_control', { action: 'pause', music_id: musicId }); };
        btnStop.onclick = function() { socket.emit('music_control', { action: 'stop', music_id: musicId }); };
        controls.appendChild(btnPlay);
        controls.appendChild(btnPause);
        controls.appendChild(btnStop);
        card.appendChild(header);
        card.appendChild(controls);
        card.appendChild(audio);
        return card;
    }
    
    // 初始调整文本框高度
    adjustTextareaHeight();
});