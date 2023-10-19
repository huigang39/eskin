import joblib
import logging
import pandas as pd
import select
import socket
import threading

import warnings
from sklearn.exceptions import ConvergenceWarning

# 设置日志格式
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

# 禁用sklearn的ConvergenceWarning警告消息
warnings.filterwarnings(action='ignore', category=ConvergenceWarning)

# 定义常量
HOST = socket.gethostname()
PORT = 2333

# 加载模型和标签映射
MODEL = joblib.load('./model/model.pkl')
LABEL_MAP = {0: '食指', 1: '小指', 2: '中指', 3: '休息', 4: '无名指', 5: '大拇指', 6: '胜利手势'}

# 定义日志
logger = logging.getLogger(__name__)


def handle_data(data):
    """处理数据并返回预测结果"""
    data = data.strip()
    lst = data.split(",")
    lst = list(map(float, lst))
    new_data = pd.DataFrame(lst).T
    y_pred = MODEL.predict(new_data)[0]
    y_pred = LABEL_MAP[y_pred]
    return y_pred


def handle_esp_conn(conn_esp, conn_flutter):
    """处理ESP32客户端连接"""
    while True:
        try:
            # 等待ESP32客户端发送数据
            data = conn_esp.recv(1024).decode()

            # 处理数据并发送预测结果
            y_pred = handle_data(data)
            if conn_flutter:
                for conn in conn_flutter:
                    try:
                        conn.send(y_pred.encode())
                    except:
                        conn_flutter.remove(conn)
            if conn_esp:
                try:
                    conn_esp.send(y_pred.encode())
                except:
                    conn_esp.close()
                    logger.info("ESP32客户端已断开连接")
                    conn_esp = None
                    conn_flutter = []
                    break
        except:
            conn_esp.close()
            logger.info("ESP32客户端已断开连接")
            conn_esp = None
            conn_flutter = []
            break


def handle_flutter_conn(conn, conn_esp, conn_flutter):
    """处理Flutter客户端连接"""
    while True:
        try:
            # 等待Flutter客户端发送数据
            data = conn.recv(1024).decode()

            # 处理数据
            ...

        except:
            conn.close()
            conn_flutter.remove(conn)
            logger.info("Flutter客户端已断开连接")
            break


def start_server():
    """启动服务器"""
    # 创建服务器套接字
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # 设置超时时间为5秒钟
        server_socket.settimeout(5)

        # 绑定到指定端口
        server_socket.bind((HOST, PORT))

        # 监听客户端连接
        server_socket.listen(5)

        # 初始化客户端连接列表
        conn_esp = None
        conn_flutter = []

        # 处理客户端连接
        while True:
            # 等待客户端连接
            logger.info("等待客户端连接...")
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue

            logger.info(f"连接来自:{str(addr)}")

            # 接收身份验证消息
            message = conn.recv(1024).decode()
            if message == "ESP32":
                # 处理ESP32客户端连接
                conn_esp = conn
                logger.info("ESP32客户端已连接")
                esp_thread = threading.Thread(
                    target=handle_esp_conn, args=(conn_esp, conn_flutter))
                esp_thread.start()
            elif message == "Flutter":
                # 处理Flutter客户端连接
                if conn_esp is None:
                    conn.send("ERROR".encode())
                    logger.info("未连接ESP32客户端")
                else:
                    conn_flutter.append(conn)
                    logger.info("Flutter客户端已连接")
                    flutter_thread = threading.Thread(
                        target=handle_flutter_conn, args=(conn, conn_esp, conn_flutter))
                    flutter_thread.start()
            else:
                logger.info("未知客户端")
    # 关闭服务器
    server_socket.close()


if __name__ == '__main__':
    start_server()

