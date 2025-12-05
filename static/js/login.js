document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const loginForm = document.getElementById('login-form');
    const loginUsernameInput = document.getElementById('login-username');
    const loginPasswordInput = document.getElementById('login-password');
    const loginServerSelect = document.getElementById('login-server');
    const loginBtn = document.getElementById('login-btn');
    
    const registerForm = document.getElementById('register-form');
    const registerUsernameInput = document.getElementById('register-username');
    const registerPasswordInput = document.getElementById('register-password');
    const registerServerSelect = document.getElementById('register-server');
    const registerBtn = document.getElementById('register-btn');
    
    const switchToRegister = document.getElementById('switch-to-register');
    const switchToLogin = document.getElementById('switch-to-login');
    
    // 从本地存储加载服务器地址
    const savedServers = JSON.parse(localStorage.getItem('servers') || '[]');
    
    // 添加默认服务器
    const defaultServers = [
        { id: 'local', name: '本地服务器', url: 'http://localhost:5000' }
    ];
    
    // 合并默认服务器和本地存储的服务器
    const allServers = [...defaultServers];
    savedServers.forEach(savedServer => {
        if (!allServers.find(server => server.url === savedServer.url)) {
            allServers.push(savedServer);
        }
    });
    
    // 填充两个服务器选择框
    allServers.forEach(server => {
        // 登录表单的服务器选择框
        const loginOption = document.createElement('option');
        loginOption.value = server.url;
        loginOption.textContent = server.name;
        loginServerSelect.appendChild(loginOption);
        
        // 注册表单的服务器选择框
        const registerOption = document.createElement('option');
        registerOption.value = server.url;
        registerOption.textContent = server.name;
        registerServerSelect.appendChild(registerOption);
    });
    
    // 表单切换功能
    switchToRegister.addEventListener('click', function() {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    });
    
    switchToLogin.addEventListener('click', function() {
        registerForm.style.display = 'none';
        loginForm.style.display = 'block';
    });
    
    // 登录按钮点击事件
    loginBtn.addEventListener('click', async function() {
        const username = loginUsernameInput.value.trim();
        const password = loginPasswordInput.value;
        
        if (!username || !password) {
            alert('请输入用户名和密码');
            return;
        }
        
        try {
            // 发送登录请求到用户选择的服务器
            const serverUrl = loginServerSelect.value;
            const response = await fetch(`${serverUrl}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 保存用户信息到本地存储
                localStorage.setItem('currentUser', JSON.stringify({ 
                    username: result.username,
                    serverUrl: loginServerSelect.value 
                }));
                
                // 重定向到聊天室页面
                window.location.href = `/chat?username=${encodeURIComponent(result.username)}`;
            } else {
                alert(result.error || '登录失败');
            }
        } catch (error) {
            console.error('登录请求失败:', error);
            alert('登录请求失败，请稍后重试');
        }
    });
    
    // 注册按钮点击事件
    registerBtn.addEventListener('click', async function() {
        const username = registerUsernameInput.value.trim();
        const password = registerPasswordInput.value;
        
        if (!username || !password) {
            alert('请输入完整的注册信息');
            return;
        }
        
        try {
            // 发送注册请求到用户选择的服务器
            const serverUrl = registerServerSelect.value;
            const response = await fetch(`${serverUrl}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('注册成功，请登录');
                // 切换回登录表单
                switchToLogin.click();
                // 填充用户名
                loginUsernameInput.value = username;
                loginPasswordInput.value = '';
            } else {
                alert(result.error || '注册失败');
            }
        } catch (error) {
            console.error('注册请求失败:', error);
            alert('注册请求失败，请稍后重试');
        }
    });
    
    // 回车登录/注册
    loginUsernameInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            loginBtn.click();
        }
    });
    
    loginPasswordInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            loginBtn.click();
        }
    });
    
    registerUsernameInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            registerBtn.click();
        }
    });
    
    registerPasswordInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            registerBtn.click();
        }
    });
    

});