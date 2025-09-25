#!/bin/bash

# 定时任务启动脚本

# 激活虚拟环境（如果使用的话）
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 设置默认执行时间（可以通过参数修改）
RUN_TIME=${1:-"09:00"}

echo "启动定时任务调度器..."
echo "执行时间: $RUN_TIME"
echo "按 Ctrl+C 停止"

# 启动调度器
python3 scheduler.py --time "$RUN_TIME"
