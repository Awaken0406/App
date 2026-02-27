import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'dart:async';
import 'dart:io';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // 强制横屏
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Number Area',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF1E1E24),
      ),
      home: const SimpleArrayDisplay(),
    );
  }
}

class SimpleArrayDisplay extends StatefulWidget {
  const SimpleArrayDisplay({super.key});

  @override
  State<SimpleArrayDisplay> createState() => _SimpleArrayDisplayState();
}

class _SimpleArrayDisplayState extends State<SimpleArrayDisplay> {

  String serverAddr = 'www.sengeapp.top';
  //String serverAddr = '127.0.0.1';



  // 原有数组
  List<int> redArray = [0, 0, 0, 0, 0, 0];
  List<int> blueArray = [0];

  // 播放状态
  bool playing = false;
  int redIndex = 0;
  int blueIndex = 0;
  int phase = 0; // 0:未播放/完成, 1:红区播放中, 2:蓝区播放中

  // 控制每个数字是否显示（用于淡入动画）
  List<bool> redVisible = [];
  List<bool> blueVisible = [];
    // 从服务器获取的描述文本
  String descriptionText = '双色球-采用大模型'; // 默认值
  // UI 状态文字
  String statusText = 'Start';
  Color statusColor = Colors.grey.shade400;
  String progressText = '';

  // 按钮状态
  bool loading = false;
  String buttonText = '来财'; // 按钮文字固定为“来财”

  // 内部状态标记（用于区分完成、错误）
  bool _isCompleted = false;
  bool _isError = false;

  // 新增：错误信息与剩余次数
  String errorMessage = '';
  int remainingQuota = 0;
  bool loadingQuota = true;

  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _initVisibility();
    _fetchQuota(); // 启动时获取剩余次数
  // 初始化 Dio 实例
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _initVisibility() {
    redVisible = List.generate(redArray.length, (_) => false);
    blueVisible = List.generate(blueArray.length, (_) => false);
  }

  void _resetState() {
    setState(() {
      redIndex = 0;
      blueIndex = 0;
      phase = 0;
      playing = false;
      _initVisibility();
      statusText = 'Start';
      statusColor = Colors.grey.shade400;
      progressText = '';
      loading = false;
      errorMessage = '';
      _isCompleted = false;
      _isError = false;
    });
  }

  void _startPlay() {
    _timer?.cancel();
    setState(() {
      playing = true;
      phase = 1;
      redIndex = 0;
      blueIndex = 0;
    });
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      _showNextNumber();
    });
  }

  void _showNextNumber() {
    if (!playing) return;

    if (phase == 1) {
      if (redIndex < redArray.length) {
        setState(() {
          redVisible[redIndex] = true;
          statusText = '${redIndex + 1} number: ${redArray[redIndex]}...';
          statusColor = const Color(0xFFFF9999);
          progressText = '${redIndex + 1}/${redArray.length} | ${blueIndex}/${blueArray.length}';
        });
        redIndex++;
        if (redIndex >= redArray.length) {
          setState(() {
            phase = 2;
            statusText = '...';
            statusColor = const Color(0xFF9999FF);
          });
          _flashRed();
        }
      }
    } else if (phase == 2) {
      if (blueIndex < blueArray.length) {
        setState(() {
          blueVisible[blueIndex] = true;
          statusText = '... ${blueIndex + 1} ...: ${blueArray[blueIndex]}';
          progressText = '...: ${redArray.length}/${redArray.length} | ...: ${blueIndex + 1}/${blueArray.length}';
        });
        blueIndex++;
        if (blueIndex >= blueArray.length) {
          _finishPlay();
        }
      }
    }
  }

  void _flashRed() {
    Future.delayed(const Duration(milliseconds: 100), () {
      setState(() {});
    });
  }

  void _finishPlay() {
    _timer?.cancel();
    setState(() {
      playing = false;
      phase = 3;
      loading = false;
      statusText = 'Done';
      statusColor = const Color(0xFFCC88CC);
      progressText = '${redArray.length}/${redArray.length} | ${blueArray.length}/${blueArray.length}';
      _isCompleted = true; // 标记为完成状态
    });
    _flashBlue();
  }

  void _flashBlue() {
    Future.delayed(const Duration(milliseconds: 100), () {
      setState(() {});
    });
  }

  // 过滤错误信息中的 IP 地址和端口
  String _filterSensitiveInfo(String errorMessage) {
    final pattern = RegExp(
      r'address\s*=\s*\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b\s*,\s*port\s*=\s*\d{2,5}',
      caseSensitive: false,
    );
    String filtered = errorMessage.replaceAll(pattern, '');
    filtered = filtered.replaceAll(RegExp(r',\s*,'), ',');
    filtered = filtered.replaceAll(RegExp(r',\s*$'), '');
    filtered = filtered.replaceAll(RegExp(r'\s+'), ' ').trim();
    return filtered;
  }

  // 获取剩余次数
  Future<void> _fetchQuota() async {
    setState(() {
      loadingQuota = true;
      errorMessage = '';
    });
    try {
      final client = HttpClient();
        //client.securityContext.allowedProtocols = [ SecurityProtocol.tls12];
        print('⚡️ badCertificateCallback 被调用了22222！');
       client.badCertificateCallback = (X509Certificate cert, String host, int port) {
        print('⚡️ badCertificateCallback 被调用了！');
        return true;
        };     
      final request = await client.getUrl(Uri.parse('https://${serverAddr}/api/quota'));
      request.headers.add('X-App-Key', 'SENGE_SECRET_KEY');
      request.headers.add('User-Agent', 'SENGEApp/1.0.0');
      final response = await request.close();

  
      if (response.statusCode == 200) {
        final stringData = await response.transform(utf8.decoder).join();
        final Map<String, dynamic> data = jsonDecode(stringData);

   
        // 解析描述文本（如果接口返回）
        if (data.containsKey('description')) {
          descriptionText = data['description'].toString();
        }
        setState(() {
          remainingQuota = data['remaining'] ?? 0;
          loadingQuota = false;
        }); 
      } else {
        setState(() {
          errorMessage = '获取剩余次数失败 (${response.statusCode})';
          loadingQuota = false;
        });
      }
      //client.close();
    } catch (e) {
      print('❌ 直接测试异常: $e');
    if (e is HandshakeException) {
      print('   HandshakeException 详情: ${e.message}');
      print('   HandshakeException 操作系统消息: ${e.osError?.message}');
    }
    if (e is SocketException) {
      print('   SocketException 详情: ${e.message}');
      print('   SocketException 操作系统错误: ${e.osError?.message}');
    }
    if (e is TlsException) {
      print('   TlsException 详情: ${e.message}');
    }
      setState(() {
        errorMessage = _filterSensitiveInfo('网络错误: $e');
        loadingQuota = false;
      });
    }
  }

  // 获取数据
  Future<void> _fetchData() async {
    setState(() {
      _resetState(); // 重置界面
      loading = true;
      _isCompleted = false;
      _isError = false;
      statusText = 'Fetching data...';
      statusColor = Colors.yellow.shade700;
      errorMessage = '';
    });

    try {
      final client = HttpClient();
      final request = await client.getUrl(Uri.parse('https://${serverAddr}/api/hello/'));
      request.headers.add('X-App-Key', 'SENGE_SECRET_KEY');
      request.headers.add('User-Agent', 'SENGEApp/1.0.0');
      final response = await request.close();
      if (response.statusCode == 200) {
        final stringData = await response.transform(utf8.decoder).join();
        final Map<String, dynamic> data = jsonDecode(stringData);

        final String redStr = data['red'];
        final String blueStr = data['blue'];
        final List<int> newRed = redStr.split(',').map(int.parse).toList();
        final List<int> newBlue = blueStr.split(',').map(int.parse).toList();

        setState(() {
          redArray = newRed;
          blueArray = newBlue;
          _initVisibility();
          statusText = 'Done !!!';
          statusColor = Colors.green;
          loading = false;
        });

        // 成功获取后重新刷新剩余次数（服务器会扣减）
        _fetchQuota();

        _startPlay();
      } else {
        setState(() {
          errorMessage = _filterSensitiveInfo('请求失败: ${response.statusCode}');
          loading = false;
          _isError = true; // 标记错误状态
        });
      }
      client.close();
    } catch (e) {
      setState(() {
        errorMessage = _filterSensitiveInfo('错误: $e');
        loading = false;
        _isError = true; // 标记错误状态
      });
    }
  }

  void _onButtonPressed() {
    if (loading) return;

    // 剩余次数为0时不允许请求
    if (remainingQuota <= 0) {
      setState(() {
        errorMessage = '今日次数已用完';
      });
      return;
    }

    // 如果处于完成或错误状态，先重置界面再获取新数据
    if (_isCompleted || _isError) {
      _resetState();
    }
    _fetchData();
  }

  // 根据状态获取按钮背景色
  Color _getButtonColor() {
    if (loading) return Colors.grey;
    if (_isCompleted) return const Color(0xFF6633CC); // 紫色
    if (_isError) return Colors.red; // 红色
    return const Color(0xFF3399CC); // 默认蓝色
  }

  @override
  Widget build(BuildContext context) {
    double screenWidth = MediaQuery.of(context).size.width;
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/background.jpg'), // 背景图路径
            fit: BoxFit.cover, // 覆盖整个屏幕
            opacity: 0.3, // 透明度，让前景内容更清晰
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(15.0),
          child: Column(
            children: [
              // 动态描述文本（替换原“双色球-采用AI大模型”）
              Text(
                descriptionText,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 10),

              // 显示剩余次数
              Text(
                loadingQuota
                    ? '获取剩余次数中...'
                    : '今日剩余次数：$remainingQuota',
                style: TextStyle(
                  fontSize: 18,
                  color: remainingQuota > 0 ? Colors.green : Colors.red,
                ),
              ),
              const SizedBox(height: 20),

              // 红区
              _buildHeaderRow(
                title: 'red',
                titleColor: const Color(0xFFFF6666),
                child: _buildNumberRow(
                  array: redArray,
                  visibleList: redVisible,
                  bgColor: const Color(0xFF6B2D2D),
                  textColor: const Color(0xFFFFCCCC),
                ),
              ),
              // 蓝区
              _buildHeaderRow(
                title: 'blue',
                titleColor: const Color(0xFF6666FF),
                child: _buildNumberRow(
                  array: blueArray,
                  visibleList: blueVisible,
                  bgColor: const Color(0xFF26264D),
                  textColor: const Color(0xFFCCCCFF),
                ),
              ),

              const SizedBox(height: 10),

              // 进度标签
              Text(
                progressText,
                style: const TextStyle(fontSize: 16, color: Color(0xFFCCCCCC)),
              ),

              const SizedBox(height: 20),

              // 播放按钮（自适应居中，文字固定为“来财”）
              Center(
                child: SizedBox(
                  width: screenWidth * 0.6,
                  child: ElevatedButton(
                    onPressed: (loading || remainingQuota <= 0) ? null : _onButtonPressed,
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                      backgroundColor: _getButtonColor(),
                      foregroundColor: Colors.white,
                      textStyle: const TextStyle(fontSize: 30),
                    ),
                    child: Text(buttonText), // 始终显示“来财”
                  ),
                ),
              ),

              const SizedBox(height: 10),

              // 错误信息显示
              Text(
                errorMessage,
                style: const TextStyle(color: Colors.red, fontSize: 16),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeaderRow({
    required String title,
    required Color titleColor,
    required Widget child,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          SizedBox(
            width: 60,
            child: Text(
              title,
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.w500, color: titleColor),
            ),
          ),
          Expanded(child: child),
        ],
      ),
    );
  }

  Widget _buildNumberRow({
    required List<int> array,
    required List<bool> visibleList,
    required Color bgColor,
    required Color textColor,
  }) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: List.generate(array.length, (index) {
          return Container(
            width: 60,
            height: 60,
            margin: const EdgeInsets.symmetric(horizontal: 5),
            decoration: BoxDecoration(shape: BoxShape.circle, color: bgColor),
            child: Center(
              child: AnimatedOpacity(
                opacity: visibleList[index] ? 1.0 : 0.0,
                duration: const Duration(milliseconds: 500),
                curve: Curves.easeIn,
                child: Text(
                  visibleList[index] ? '${array[index]}' : '',
                  style: TextStyle(
                    fontSize: 28,
                    color: textColor.withOpacity(visibleList[index] ? 1 : 0),
                    fontWeight: FontWeight.normal,
                  ),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
}