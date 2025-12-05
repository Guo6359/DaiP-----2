// 天气背景调试脚本
// 可直接在浏览器控制台中运行

// 模拟接收天气消息
function simulateWeatherMessage(weatherType) {
    console.log('=== 模拟天气消息 ===');
    console.log('天气类型:', weatherType);
    
    // 调用setWeatherBackground函数
    if (typeof setWeatherBackground === 'function') {
        setWeatherBackground(weatherType);
        console.log('调用了setWeatherBackground函数');
        console.log('当前body类:', document.body.className);
        console.log('chat-main背景:', window.getComputedStyle(document.querySelector('.chat-main')).background);
    } else {
        console.error('setWeatherBackground函数未定义');
    }
}

// 测试所有天气类型
function testAllWeatherTypes() {
    console.log('=== 测试所有天气类型 ===');
    const weatherTypes = ['晴', '多云', '阴', '小雨', '雪', '雾', '霾', '雷阵雨'];
    
    weatherTypes.forEach((type, index) => {
        setTimeout(() => {
            console.log(`\n--- 测试第${index + 1}/${weatherTypes.length}个天气类型: ${type} ---`);
            simulateWeatherMessage(type);
        }, index * 1000);
    });
}

// 检查DOM结构
function checkDOMStructure() {
    console.log('=== 检查DOM结构 ===');
    const chatMain = document.querySelector('.chat-main');
    const body = document.body;
    
    console.log('body元素存在:', body ? '是' : '否');
    console.log('chat-main元素存在:', chatMain ? '是' : '否');
    console.log('chat-main样式:', chatMain ? window.getComputedStyle(chatMain) : '不存在');
    console.log('当前body类:', body.className);
}

// 清除所有天气类
function clearAllWeatherClasses() {
    const weatherClasses = ['weather-sunny', 'weather-cloudy', 'weather-rainy', 'weather-snowy', 'weather-foggy', 'weather-stormy'];
    const body = document.body;
    
    weatherClasses.forEach(cls => {
        body.classList.remove(cls);
    });
    
    console.log('已清除所有天气类');
    console.log('当前body类:', body.className);
}

// 手动添加天气类
function addWeatherClass(weatherClass) {
    const body = document.body;
    body.classList.add(weatherClass);
    console.log(`已添加天气类: ${weatherClass}`);
    console.log('当前body类:', body.className);
    console.log('chat-main背景:', window.getComputedStyle(document.querySelector('.chat-main')).background);
}

// 暴露测试函数到全局
window.simulateWeatherMessage = simulateWeatherMessage;
window.testAllWeatherTypes = testAllWeatherTypes;
window.checkDOMStructure = checkDOMStructure;
window.clearAllWeatherClasses = clearAllWeatherClasses;
window.addWeatherClass = addWeatherClass;

console.log('=== 天气背景调试脚本已加载 ===');
console.log('可用的测试函数:');
console.log('simulateWeatherMessage("晴") - 模拟特定天气类型');
console.log('testAllWeatherTypes() - 依次测试所有天气类型');
console.log('checkDOMStructure() - 检查DOM结构和样式');
console.log('clearAllWeatherClasses() - 清除所有天气类');
console.log('addWeatherClass("weather-sunny") - 手动添加天气类');
