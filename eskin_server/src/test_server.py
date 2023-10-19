import joblib
import pandas as pd
import socket


def start_server(label_map, model):
    host = socket.gethostname()
    ip_address = socket.gethostbyname(host)
    port = 2333

    server_socket = socket.socket()
    server_socket.bind((ip_address, port))

    server_socket.listen(2)  # 接受两个客户端

    conn_esp = None
    conn_flutter = None

    while True:
        # 等待客户端连接
        print("等待客户端连接...")
        conn, addr = server_socket.accept()
        print(f"连接来自：{str(addr)}")

        # 接收身份验证消息
        message = conn.recv(1024).decode()
        if message == "ESP32":
            conn_esp = conn
            print("ESP32 客户端已连接")
        elif message == "Flutter":
            conn_flutter = conn
            print("Flutter 客户端已连接")
        else:
            print("未知客户端")

        # 如果已经连接了两个客户端，则开始接收 ESP32 发送的数据
        if conn_esp and conn_flutter:
            while True:
                # 接收来自 ESP32 客户端的数据
                data = conn_esp.recv(1024).decode()
                print(f"接收到的数据：{data}")

                data = data.strip()

                # 将字符串转换为列表
                lst = data.split(",")

                # 将字符串转换为 float 类型
                lst = list(map(float, lst))

                # 将值传递给 DataFrame 函数
                new_data = pd.DataFrame(lst).T

                y_pred = model.predict(new_data)[0]
                y_pred = label_map[y_pred]

                # 将预测结果发送给 Flutter 客户端
                conn_flutter.send(y_pred.encode())

            # 关闭连接
            conn_esp.close()
            conn_flutter.close()
            break


if __name__ == '__main__':
    label_map = {0: '食指', 1: '小指', 2: '中指',
                 3: '休息', 4: '无名指', 5: '大拇指', 6: '胜利手势'}

    model = joblib.load('model/model.pkl')

    start_server(label_map, model)
