#!/bin/bash
# 停止API服务脚本

echo "正在查找API服务进程..."
PID=$(pgrep -f "api.py|uvicorn.*api:app")

if [ -n "$PID" ]; then
    echo "找到进程 $PID，正在关闭..."
    kill -TERM $PID
    sleep 2
    
    # 检查是否成功关闭
    if kill -0 $PID 2>/dev/null; then
        echo "进程仍在运行，强制关闭..."
        kill -9 $PID
    fi
    
    echo "API服务已关闭"
else
    echo "未找到运行中的API服务"
fi