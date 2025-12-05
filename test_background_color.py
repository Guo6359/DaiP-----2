#!/usr/bin/env python3
"""
测试背景颜色变化功能的详细诊断脚本
"""

import time
import requests
from socketio import Client

sio = Client()

# 测试结果记录
test_results = {
    "server_status": None,
    "socketio_connection": None,
    "weather_query_response": None,
    "weather_type_received": None,
    "test_passed": False
}

# Socket.IO事件处理
@sio.event
def connect():
    print("✓ Socket.IO连接成功")
    test_results["socketio_connection"] = True
    
    # 发送join事件加入聊天室
    print("发送join事件加入聊天室")
    sio.emit('join', {"username": "test_background_user"})

# 用户在线事件处理
@sio.event
def user_online(data):
    print(f"用户状态更新: {data}")
    
    # 用户加入房间后发送天气查询
    print("发送天气查询: @天气 北京")
    sio.emit('send_message', {"message": "@天气 北京"})

@sio.event
def disconnect():
    print("Socket.IO连接断开")

@sio.event
def new_message(data):
    print(f"\n收到消息: {data}")
    test_results["weather_query_response"] = data
    
    # 检查是否包含weather_type字段
    if "weather_type" in data:
        print(f"✓ 消息包含weather_type字段: {data['weather_type']}")
        test_results["weather_type_received"] = data['weather_type']
        test_results["test_passed"] = True
        
        # 断开连接
        sio.disconnect()
    else:
        print("✗ 消息不包含weather_type字段")
        test_results["weather_type_received"] = False
        test_results["test_passed"] = False
        
        # 断开连接
        sio.disconnect()

@sio.event
def connect_error(data):
    print(f"✗ Socket.IO连接错误: {data}")
    test_results["socketio_connection"] = False
    test_results["test_passed"] = False
    sio.disconnect()

# 主测试函数
def main():
    print("开始诊断背景颜色变化问题...\n")
    
    # 1. 测试服务器HTTP响应
    print("1. 测试服务器HTTP状态...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✓ 服务器HTTP响应正常")
            test_results["server_status"] = True
        else:
            print(f"✗ 服务器HTTP响应错误，状态码: {response.status_code}")
            test_results["server_status"] = False
            return
    except Exception as e:
        print(f"✗ 无法连接到服务器: {e}")
        test_results["server_status"] = False
        return
    
    # 2. 测试Socket.IO连接
    print("\n2. 测试Socket.IO连接...")
    try:
        sio.connect("http://localhost:5000")
        # 等待消息响应
        sio.wait()
    except Exception as e:
        print(f"✗ Socket.IO连接失败: {e}")
        test_results["socketio_connection"] = False
        return
    
    # 3. 输出测试报告
    print("\n" + "="*50)
    print("测试报告")
    print("="*50)
    
    print(f"服务器状态: {'✓ 正常' if test_results['server_status'] else '✗ 异常'}")
    print(f"Socket.IO连接: {'✓ 成功' if test_results['socketio_connection'] else '✗ 失败'}")
    
    if test_results['weather_query_response']:
        print(f"收到响应: {test_results['weather_query_response']}")
        if test_results['weather_type_received']:
            print(f"Weather_type字段: {test_results['weather_type_received']}")
            print("\n结论: 服务器端发送天气消息正常，包含weather_type字段")
            print("问题可能出在客户端JavaScript代码或CSS样式上")
        else:
            print("\n结论: 服务器返回的消息不包含weather_type字段")
            print("问题出在服务器端消息构建逻辑")
    else:
        print("\n结论: 未收到天气查询响应")
        print("问题可能出在Socket.IO消息处理或服务器路由")
    
    print("\n建议下一步:")
    print("1. 检查客户端浏览器控制台是否有JavaScript错误")
    print("2. 验证客户端setWeatherBackground函数是否被调用")
    print("3. 检查CSS样式是否正确加载")

if __name__ == "__main__":
    main()
