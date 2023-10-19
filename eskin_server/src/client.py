import socket

host = '20.189.79.217'
port = 2333

client_socket = socket.socket()
client_socket.connect((host, port))

# 接收服务端返回的预测结果
result = client_socket.recv(1024)
print(result.decode())

client_socket.close()
