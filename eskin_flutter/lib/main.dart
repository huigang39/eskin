import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'E-Skin',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(title: '手势信号识别'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _serverResponse = '';
  Color? _randomColor = Colors.blue;
  late SharedPreferences _prefs;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() async {
    _prefs = await SharedPreferences.getInstance();
    final ipAddress = _prefs.getString('ipAddress');
    final portNumber = _prefs.getInt('portNumber');
    if (ipAddress != null && portNumber != null) {
      _connectToServer(ipAddress, portNumber);
    }
  }

  void _connectToServer(String ipAddress, int portNumber) async {
    try {
      final socket = await Socket.connect(ipAddress, portNumber);

      // 发送身份验证消息
      String message = "Flutter";
      socket.write(message);

      socket.listen((List<int> event) {
        setState(() {
          _serverResponse = utf8.decode(event);
          switch (_serverResponse) {
            case '食指':
              _randomColor = Colors.red;
              break;
            case '小指':
              _randomColor = Colors.green;
              break;
            case '中指':
              _randomColor = Colors.blue;
              break;
            case '休息':
              _randomColor = Colors.grey;
              break;
            case '无名指':
              _randomColor = Colors.purple;
              break;
            case '大拇指':
              _randomColor = Colors.yellow;
              break;
            case '胜利手势':
              _randomColor = Colors.orange;
              break;
            default:
              _randomColor = Colors.blue;
          }
        });
      });
    } catch (e) {
      print('Error: $e');
    }
  }

  void _clearData() async {
    await _prefs.remove('ipAddress');
    await _prefs.remove('portNumber');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: <Widget>[
          IconButton(
            icon: Icon(Icons.delete),
            onPressed: () {
              _clearData();
            },
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Spacer(),
            Text(
              '识别手势为: $_serverResponse',
              style: TextStyle(
                color: _randomColor,
                fontSize: 24.0,
                fontWeight: FontWeight.bold,
              ),
            ),
            Spacer(),
            Image.asset(
              _serverResponse == '食指'
                  ? 'images/index_finger.png'
                  : (_serverResponse == '小指'
                      ? 'images/little_finger.png'
                      : (_serverResponse == '中指'
                          ? 'images/middle_finger.png'
                          : (_serverResponse == '休息'
                              ? 'images/rest.png'
                              : (_serverResponse == '无名指'
                                  ? 'images/ring_finger.png'
                                  : (_serverResponse == '大拇指'
                                      ? 'images/thumb.png'
                                      : (_serverResponse == '胜利手势'
                                          ? 'images/victory_gesture.png'
                                          : 'images/rest.png')))))),
              height: 200.0,
              width: 200.0,
            ),
            Spacer(),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SettingsPage(),
            ),
          );
          if (result != null) {
            final ipAddress = result['ipAddress'];
            final portNumber = result['portNumber'];
            _connectToServer(ipAddress, portNumber);
          }
        },
        child: Icon(Icons.settings),
      ),
    );
  }
}

class SettingsPage extends StatefulWidget {
  @override
  State<StatefulWidget> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  late SharedPreferences _prefs;
  final _ipController = TextEditingController();
  final _portController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() async {
    _prefs = await SharedPreferences.getInstance();
    final ipAddress = _prefs.getString('ipAddress');
    final portNumber = _prefs.getInt('portNumber');
    if (ipAddress != null) {
      _ipController.text = ipAddress;
    }
    if (portNumber != null) {
      _portController.text = portNumber.toString();
    }
  }

  void _saveData() async {
    if (_formKey.currentState!.validate()) {
      await _prefs.setString('ipAddress', _ipController.text);
      await _prefs.setInt('portNumber', int.parse(_portController.text));
      Navigator.pop(context, {
        'ipAddress': _ipController.text,
        'portNumber': int.parse(_portController.text),
      });
    }
  }

  @override
  Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: Text('设置'),
    ),
    body: Padding(
      padding: EdgeInsets.all(16.0),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            TextFormField(
              controller: _ipController,
              decoration: InputDecoration(
                labelText: '服务器 IP 地址',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20.0),
                ),
              ),
              validator: (value) {
                if (value!.isEmpty) {
                  return '请输入服务器 IP 地址';
                }
                final parts = value.split('.');
                if (parts.length != 4 ||
                    parts.any((part) =>
                        int.tryParse(part) == null ||
                        int.parse(part) < 0 ||
                        int.parse(part) > 255)) {
                  return '请输入正确的 IP 地址';
                }
                return null;
              },
            ),
            ClipRRect(
              borderRadius: BorderRadius.circular(10.0),
              child: SizedBox(
                height: 16.0,
              ),
            ),
            TextFormField(
              controller: _portController,
              decoration: InputDecoration(
                labelText: '端口号',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20.0),
                ),
              ),
              validator: (value) {
                if (value!.isEmpty) {
                  return '请输入端口号';
                }
                final portNumber = int.tryParse(value);
                if (portNumber == null || portNumber < 0 || portNumber > 65535) {
                  return '请输入正确的端口号';
                }
                return null;
              },
            ),
            ClipRRect(
              borderRadius: BorderRadius.circular(10.0),
              child: SizedBox(
                height: 16.0,
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: <Widget>[
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20.0),
                    ),
                  ),
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  child: Text('取消'),
                ),
                SizedBox(
                  width: 16.0,
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20.0),
                    ),
                  ),
                  onPressed: () {
                    _saveData();
                  },
                  child: Text('保存'),
                ),
              ],
            ),
          ],
        ),
      ),
    ),
  );
  }
}
