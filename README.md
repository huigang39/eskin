
# 断指-电子皮肤

## 系统框架流程

1. 信号读取

使用 ESP 32 的 ADC 外设读取电极输出的电压，截取一段原始电压数据进行打包，并通过 socket 通信向服务器公网 IP 发送。

2. 信号处理

服务器通过 socket 通信接收 ESP 32 发送过来的原始电压数据，对其进行特征值提取，随后即将特征值输入分类模型内对其进行分类，分类结果通过 socket 通信发送到 Flutter 客户端和 ESP 32 设备端。

3. 结果输出

在 Flutter 客户端 APP 通过 socket 通信接收来自服务端的分类结果，并切换对应图片进行直观展示，同时 ESP 32 设备端也会接收来自服务端的结果，并驱动对应舵机带动手指。

系统流程图如下：

开发环境：
设备端：ESP 32 DevkitC-1 开发板
服务端：Microsoft Azure 虚拟机（Ubuntu 系统）
客户端：Flutter 跨平台框架

```mermaid
graph LR

电子皮肤 --输出信号--> 设备端

设备端 --发送数据--> 服务端
设备端 --控制--> 断指辅具

服务端 --返回结果--> 设备端
服务端 --返回结果--> 客户端
```

下面将详细介绍各模块设计与实现。

## 设计与实现

### 设备端

[电子皮肤/断指ESP32程序](https://github.com/huigang39/eskin_esp32)

该模块使用 PlatformIO 开发，若使用 Arduino IDE 复现或二次开发本模块，将 `src` 文件夹中的 `main.cpp` 改为 `main.ino` 即可编译。

> 如果安装时，舵机绑线位置不对，可以通过修改舵机初始角度和转动角度在软件层面调整。

程序逻辑图如下：

```mermaid
graph LR
A[开始] --> B(连接WiFi)
B --> C{是否连接成功?}
C -->|是| D[启动定时器]
C -->|否| B
D --> E{是否采样完数据?}
E -->|是| F[发送数据包]
E -->|否| G[采样数据]
F --> H{是否收到响应?}
H -->|是| I[解析响应]
H -->|否| F
I --> J{是否需要控制手指舵机?}
J -->|是| K[控制手指舵机]
J -->|否| E
K --> E
```

### 服务端

[电子皮肤/断指服务端程序](https://github.com/huigang39/eskin_server)

该模块主要分为两个部分：

第一部分是训练模型，主要通过 `sklearn` 中的随机森林分类器来对 `data` 文件夹下的数据进行训练，并输出模型到 `model` 文件夹。

第二部分是部署模型，该部分通过接收设备端的原始数据，通过 `server.py` 处理并返回模型的输出分类标签到设备端和客户端。

程序逻辑图如下：

```mermaid
graph LR
A[创建服务器套接字] --> B[绑定到指定端口]
B --> C[监听客户端连接]
C --> D[等待客户端连接]
D --> |ESP32客户端连接请求| E[处理ESP32客户端连接]
D --> |Flutter客户端连接请求| F[处理Flutter客户端连接]
E --> G[等待ESP32客户端发送数据]
G --> H[处理数据并发送预测结果]
H --> I{是否有Flutter客户端连接?}
I --> |是| J[发送预测结果到所有Flutter客户端]
I --> |否| G
J --> K{是否发送成功?}
K --> |是| L[继续等待ESP32客户端发送数据]
K --> |否| M[从连接列表中移除连接]
F --> N[等待Flutter客户端发送数据]
N --> O{是否有ESP32客户端连接?}
O --> |是| P[处理数据]
P --> Q{是否需要发送控制指令?}
Q --> |是| R[发送控制指令到ESP32客户端]
Q --> |否| N
O --> |否| S[从连接列表中移除连接]
```

### 客户端

[电子皮肤/断指Flutter程序](https://github.com/huigang39/eskin_flutter)

该模块使用 Flutter 跨平台软件开发框架，不推荐复现本模块，因为环境配置较为繁琐。

程序逻辑图如下：

```mermaid
graph LR
A[创建SharedPreferences实例] --> B[读取服务器IP地址和端口号]
B --> C[连接服务器]
C --> D{是否连接成功?}
D --> |是| E[发送身份验证消息]
D --> |否| F[显示连接失败提示]
E --> F[显示连接成功提示]
E --> G[等待服务器数据]
G --> H{是否收到数据?}
H --> |是| I[解析数据并更新UI]
H --> |否| G
I --> J[根据数据更新UI]
J --> K{是否需要发送控制指令?}
K --> |是| L[发送控制指令到服务器]
K --> |否| G
L --> M{是否发送成功?}
M --> |是| G
M --> |否| N[显示发送失败提示]
F --> O[显示错误]
O --> P[关闭连接并重试]
N --> P
P --> C
```
