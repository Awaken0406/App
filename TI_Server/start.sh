#!/bin/bash
# 脚本功能：后台启动Server.py，日志输出到log.log，包含进程管理功能
# 使用方式：chmod +x start_server.sh && ./start_server.sh start/stop/restart/status

# 配置项（根据你的实际路径修改）
PYTHON_PATH="/usr/bin/python3"  # python解释器路径
SERVER_SCRIPT="./Server.py"  # Server.py的绝对路径
LOG_FILE="./log.log"  # 日志文件路径
PID_FILE="/tmp/server.pid"  # 进程ID文件，用于管理进程

# 启动函数
start() {
    # 检查Server.py是否存在
    if [ ! -f "$SERVER_SCRIPT" ]; then
        echo "错误：找不到Server.py文件，路径：$SERVER_SCRIPT"
        exit 1
    fi

    # 检查是否已在运行
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Server.py已在运行，进程ID：$PID"
            exit 0
        else
            # PID文件存在但进程不存在，删除PID文件
            rm -f "$PID_FILE"
        fi
    fi

    # 后台启动脚本，将标准输出和标准错误都写入日志
    echo "启动Server.py...日志将写入：$LOG_FILE"
    nohup "$PYTHON_PATH" "$SERVER_SCRIPT" > "$LOG_FILE" 2>&1 &
    # 保存进程ID到PID文件
    echo $! > "$PID_FILE"

    # 验证启动是否成功
    sleep 2
    if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "Server.py启动成功，进程ID：$(cat "$PID_FILE")"
    else
        echo "错误：Server.py启动失败，请查看日志：$LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# 停止函数
stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Server.py未运行（无PID文件）"
        exit 0
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "停止Server.py，进程ID：$PID"
        kill "$PID"
        # 等待进程退出
        sleep 3
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "强制终止进程..."
            kill -9 "$PID"
        fi
        rm -f "$PID_FILE"
        echo "Server.py已停止"
    else
        echo "Server.py进程不存在，删除无效PID文件"
        rm -f "$PID_FILE"
    fi
}

# 重启函数
restart() {
    stop
    start
}

# 状态检查函数
status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Server.py正在运行，进程ID：$PID"
        else
            echo "Server.py已停止，但PID文件未清理"
        fi
    else
        echo "Server.py未运行"
    fi
}

# 命令参数判断
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "使用方法：$0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0