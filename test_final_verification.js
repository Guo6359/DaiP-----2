// 天气背景颜色变化最终验证脚本
// 可在浏览器控制台中运行

// 步骤1: 检查DOM结构
console.log('=== 步骤1: 检查DOM结构 ===');
const body = document.body;
const chatMain = document.querySelector('.chat-main');

if (!body || !chatMain) {
    console.error('DOM结构不完整，无法继续测试');
    throw new Error('DOM结构不完整');
}

console.log('✓ body元素存在');
console.log('✓ chat-main元素存在');

// 步骤2: 测试setWeatherBackground函数
console.log('\n=== 步骤2: 测试setWeatherBackground函数 ===');

if (typeof setWeatherBackground !== 'function') {
    console.error('setWeatherBackground函数未定义');
    throw new Error('setWeatherBackground函数未定义');
}

console.log('✓ setWeatherBackground函数已定义');

// 步骤3: 测试单个天气类型
console.log('\n=== 步骤3: 测试单个天气类型 ===');

function testSingleWeatherType(weatherType, expectedClass) {
    // 清除所有天气类
    const weatherClasses = ['weather-sunny', 'weather-cloudy', 'weather-rainy', 'weather-snowy', 'weather-foggy', 'weather-stormy'];
    weatherClasses.forEach(cls => body.classList.remove(cls));
    
    console.log(`测试天气类型: ${weatherType}`);
    console.log(`预期CSS类: ${expectedClass}`);
    
    // 调用函数
    setWeatherBackground(weatherType);
    
    // 检查类是否添加
    const hasClass = body.classList.contains(expectedClass);
    console.log(`body是否包含类${expectedClass}: ${hasClass ? '是 ✓' : '否 ✗'}`);
    
    // 检查背景颜色
    const computedBg = window.getComputedStyle(chatMain).background;
    console.log(`chat-main计算背景: ${computedBg}`);
    
    return hasClass;
}

// 测试晴天
const sunnyTest = testSingleWeatherType('晴', 'weather-sunny');

// 步骤4: 测试所有天气类型
console.log('\n=== 步骤4: 测试所有天气类型 ===');

const weatherTests = [
    { type: '晴', expected: 'weather-sunny' },
    { type: '多云', expected: 'weather-cloudy' },
    { type: '阴', expected: 'weather-cloudy' },
    { type: '小雨', expected: 'weather-rainy' },
    { type: '雪', expected: 'weather-snowy' },
    { type: '雾', expected: 'weather-foggy' },
    { type: '霾', expected: 'weather-foggy' },
    { type: '雷阵雨', expected: 'weather-stormy' }
];

let passedTests = 0;

weatherTests.forEach((test, index) => {
    const result = testSingleWeatherType(test.type, test.expected);
    if (result) passedTests++;
    
    // 为下一个测试添加短暂延迟
    if (index < weatherTests.length - 1) {
        console.log('---');
    }
});

// 步骤5: 模拟天气消息
console.log('\n=== 步骤5: 模拟天气消息 ===');

// 模拟从服务器接收的天气消息
function simulateWeatherMessage(weatherType) {
    console.log(`模拟接收天气消息，天气类型: ${weatherType}`);
    
    // 清除所有天气类
    const weatherClasses = ['weather-sunny', 'weather-cloudy', 'weather-rainy', 'weather-snowy', 'weather-foggy', 'weather-stormy'];
    weatherClasses.forEach(cls => body.classList.remove(cls));
    
    // 触发new_message事件处理逻辑
    const eventData = {
        username: '系统',
        message: `北京天气：${weatherType}`,
        weather_type: weatherType
    };
    
    console.log('模拟事件数据:', eventData);
    
    // 直接调用new_message事件处理逻辑
    const isUser = eventData.username === username;
    addMessage(eventData.username, eventData.message, false, isUser, eventData.is_movie, eventData.movie_url);
    
    if (eventData.weather_type) {
        console.log('调用setWeatherBackground函数');
        setWeatherBackground(eventData.weather_type);
        console.log(`最终body类: ${body.className}`);
        console.log(`chat-main背景: ${window.getComputedStyle(chatMain).background}`);
    }
}

// 步骤6: 总结测试结果
console.log('\n=== 步骤6: 总结测试结果 ===');

console.log(`总测试数: ${weatherTests.length}`);
console.log(`通过测试数: ${passedTests}`);
console.log(`失败测试数: ${weatherTests.length - passedTests}`);

if (passedTests === weatherTests.length) {
    console.log('🎉 所有测试都通过了！天气背景变化功能正常工作。');
} else {
    console.log('❌ 有测试失败，请检查代码。');
}

// 步骤7: 使用方法提示
console.log('\n=== 步骤7: 使用方法 ===');
console.log('您可以在聊天框中发送以下格式的消息来测试天气功能：');
console.log('@天气 北京');
console.log('@天气 上海');
console.log('@天气 广州');
console.log('@天气 深圳');
console.log('@天气 成都');
console.log('@天气 杭州');
console.log('@天气 西安');

// 暴露函数到全局，方便手动测试
window.testWeatherBackground = testSingleWeatherType;
window.testAllWeatherTypes = () => {
    weatherTests.forEach(test => testSingleWeatherType(test.type, test.expected));
};
window.simulateWeatherMessage = simulateWeatherMessage;

console.log('\n=== 验证脚本执行完成 ===');
console.log('您可以使用以下全局函数进行进一步测试：');
console.log('- testWeatherBackground(weatherType, expectedClass) - 测试单个天气类型');
console.log('- testAllWeatherTypes() - 测试所有天气类型');
console.log('- simulateWeatherMessage(weatherType) - 模拟天气消息');
