// 这是一个模拟浏览器环境的测试脚本，用于在浏览器控制台中运行
// 可以直接复制到浏览器开发者工具的控制台执行

// 测试配置
const TEST_CONFIG = {
    username: 'browser_test_user',
    testMessages: ['@天气 北京', '@天气 上海', '@天气 广州'],
    delayBetweenMessages: 1000, // 消息间延迟1秒
    maxWaitTime: 10000, // 最大等待时间10秒
    logLevel: 'verbose' // verbose, info, error
};

// 测试状态
const testState = {
    connectionStatus: 'disconnected',
    username: '',
    messagesSent: 0,
    messagesReceived: 0,
    errors: 0,
    startTime: null,
    weatherBackgroundApplied: false,
    lastWeatherType: null,
    socketEvents: [],
    domInteractions: []
};

// 日志函数
function log(message, level = 'info') {
    if (level === 'error' || 
        (level === 'info' && TEST_CONFIG.logLevel !== 'error') || 
        (level === 'verbose' && TEST_CONFIG.logLevel === 'verbose')) {
        const timestamp = new Date().toLocaleTimeString();
        const color = level === 'error' ? '#ff4444' : level === 'verbose' ? '#888888' : '#2196f3';
        console.log(`%c[${timestamp}] ${message}`, `color: ${color};`);
    }
}

// 检查DOM元素
function checkDOMElements() {
    const requiredElements = [
        'message-input',
        'send-btn',
        'chat-messages',
        'users-container',
        'logout-btn'
    ];
    
    let allPresent = true;
    requiredElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            log(`✓ DOM元素存在: #${id}`, 'verbose');
        } else {
            log(`✗ DOM元素缺失: #${id}`, 'error');
            allPresent = false;
        }
    });
    
    return allPresent;
}

// 检查Socket.IO连接状态
function checkSocketConnection() {
    if (window.socket) {
        if (window.socket.connected) {
            log('✓ Socket.IO连接状态: 已连接', 'info');
            testState.connectionStatus = 'connected';
            return true;
        } else {
            log('⚠ Socket.IO连接状态: 已断开', 'info');
            testState.connectionStatus = 'disconnected';
            return false;
        }
    } else {
        log('✗ Socket.IO实例未找到', 'error');
        testState.connectionStatus = 'not_found';
        return false;
    }
}

// 记录Socket.IO事件
function hookSocketEvents() {
    if (!window.socket) return;
    
    const originalEmit = window.socket.emit;
    window.socket.emit = function(eventName, data) {
        log(`↗ 发送Socket事件: ${eventName}`, 'verbose');
        testState.socketEvents.push({
            type: 'emit',
            eventName,
            data,
            timestamp: Date.now()
        });
        return originalEmit.apply(this, arguments);
    };
    
    // 监听关键事件
    ['connect', 'disconnect', 'new_message', 'user_online', 'user_offline'].forEach(event => {
        window.socket.on(event, function(data) {
            log(`↘ 接收Socket事件: ${event}`, 'verbose');
            testState.socketEvents.push({
                type: 'on',
                eventName: event,
                data,
                timestamp: Date.now()
            });
            
            // 特别关注new_message事件
            if (event === 'new_message') {
                testState.messagesReceived++;
                if (data.weather_type) {
                    log(`🌤 天气类型更新: ${data.weather_type}`, 'info');
                    testState.weatherBackgroundApplied = true;
                    testState.lastWeatherType = data.weather_type;
                }
            }
        });
    });
    
    log('✓ Socket.IO事件钩子已安装', 'info');
}

// 发送测试消息
function sendTestMessage(message, index) {
    return new Promise((resolve, reject) => {
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        
        if (!messageInput || !sendBtn) {
            reject(new Error('消息输入框或发送按钮未找到'));
            return;
        }
        
        try {
            // 模拟用户输入
            messageInput.value = message;
            log(`✍ 输入消息 #${index + 1}: ${message}`, 'info');
            
            // 触发输入事件
            messageInput.dispatchEvent(new Event('input', { bubbles: true }));
            
            // 点击发送按钮
            sendBtn.click();
            log(`📤 发送消息 #${index + 1}`, 'info');
            
            testState.messagesSent++;
            testState.domInteractions.push({
                action: 'send_message',
                message,
                index,
                timestamp: Date.now()
            });
            
            resolve();
        } catch (error) {
            log(`❌ 发送消息 #${index + 1}失败: ${error.message}`, 'error');
            testState.errors++;
            reject(error);
        }
    });
}

// 检查页面响应性
function checkPageResponsiveness() {
    const startTime = Date.now();
    
    // 尝试执行一个简单的DOM操作
    const testElement = document.createElement('div');
    testElement.style.display = 'none';
    document.body.appendChild(testElement);
    document.body.removeChild(testElement);
    
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    if (responseTime < 100) {
        log(`✓ 页面响应时间: ${responseTime}ms (正常)`, 'info');
        return true;
    } else {
        log(`⚠ 页面响应时间: ${responseTime}ms (较慢)`, 'warning');
        return false;
    }
}

// 运行完整测试
async function runCompleteTest() {
    log('🚀 开始浏览器环境完整性测试', 'info');
    log(JSON.stringify(TEST_CONFIG, null, 2), 'verbose');
    
    testState.startTime = Date.now();
    
    // 1. 检查DOM元素
    log('\n1. 检查DOM元素', 'info');
    if (!checkDOMElements()) {
        log('❌ 缺少必要的DOM元素，测试中止', 'error');
        return;
    }
    
    // 2. 检查Socket连接
    log('\n2. 检查Socket.IO连接', 'info');
    if (!checkSocketConnection()) {
        log('❌ Socket连接异常，测试中止', 'error');
        return;
    }
    
    // 3. 安装Socket事件钩子
    log('\n3. 安装Socket.IO事件钩子', 'info');
    hookSocketEvents();
    
    // 4. 开始发送测试消息
    log('\n4. 发送测试消息', 'info');
    
    for (let i = 0; i < TEST_CONFIG.testMessages.length; i++) {
        const message = TEST_CONFIG.testMessages[i];
        
        try {
            await sendTestMessage(message, i);
            
            // 等待一段时间再发送下一条消息
            if (i < TEST_CONFIG.testMessages.length - 1) {
                log(`⏱ 等待 ${TEST_CONFIG.delayBetweenMessages}ms 发送下一条消息`, 'verbose');
                await new Promise(resolve => setTimeout(resolve, TEST_CONFIG.delayBetweenMessages));
            }
        } catch (error) {
            log(`❌ 消息 #${i + 1}发送失败: ${error.message}`, 'error');
            continue;
        }
        
        // 检查页面响应性
        checkPageResponsiveness();
    }
    
    // 5. 等待响应完成
    log('\n5. 等待所有响应完成', 'info');
    const waitStartTime = Date.now();
    
    while (testState.messagesReceived < testState.messagesSent) {
        if (Date.now() - waitStartTime > TEST_CONFIG.maxWaitTime) {
            log('❌ 等待超时，未收到所有响应', 'error');
            break;
        }
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    // 6. 检查天气背景应用情况
    log('\n6. 检查天气背景应用', 'info');
    if (testState.weatherBackgroundApplied) {
        log(`✓ 天气背景已应用: ${testState.lastWeatherType}`, 'info');
        log(`✓ 当前body类: ${document.body.className}`, 'verbose');
    } else {
        log('⚠ 天气背景未应用', 'warning');
    }
    
    // 7. 生成测试报告
    log('\n=== 浏览器环境测试报告 ===', 'info');
    log(`测试持续时间: ${Date.now() - testState.startTime}ms`, 'info');
    log(`发送消息数量: ${testState.messagesSent}`, 'info');
    log(`接收消息数量: ${testState.messagesReceived}`, 'info');
    log(`发生错误数量: ${testState.errors}`, 'info');
    log(`连接状态: ${testState.connectionStatus}`, 'info');
    log(`天气背景应用: ${testState.weatherBackgroundApplied ? '是' : '否'}`, 'info');
    
    if (testState.messagesReceived === testState.messagesSent && testState.errors === 0) {
        log('✅ 所有测试通过!', 'info');
    } else {
        log('❌ 测试部分失败，请检查上述日志', 'error');
        log('\n💡 可能的问题：', 'info');
        log('1. 浏览器兼容性问题（特别是backdrop-filter属性）', 'info');
        log('2. CSS样式冲突导致页面元素不可交互', 'info');
        log('3. Socket.IO连接不稳定', 'info');
        log('4. 消息发送频率过快导致服务器处理延迟', 'info');
    }
    
    return testState;
}

// 暴露测试函数到全局
window.runWeatherTest = runCompleteTest;

log('📋 浏览器测试脚本已加载!', 'info');
log('🔧 执行 window.runWeatherTest() 开始测试', 'info');
