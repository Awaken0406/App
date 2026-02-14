import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:async';
import 'dart:io';

void main() => runApp(const MyApp());

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

  // UI 状态文字
  String statusText = 'Start';
  Color statusColor = Colors.grey.shade400;
  String progressText = '';

  // 按钮状态
  bool loading = false;
  String buttonText = 'Start';

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
      buttonText = 'Start';
      loading = false;
      errorMessage = ''; // 清空错误
    });
  }

  void _startPlay() {
    _timer?.cancel();
    setState(() {
      playing = true;
      phase = 1;
      redIndex = 0;
      blueIndex = 0;
      buttonText = '...';
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
      buttonText = 'Replay';
      loading = false;
      statusText = 'Done';
      statusColor = const Color(0xFFCC88CC);
      progressText = '${redArray.length}/${redArray.length} | ${blueArray.length}/${blueArray.length}';
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
    // 匹配类似 "错误连接,address = 127.0.0.1,port = 59109" 中的 address 和 port 部分
      // 这个正则匹配从 "address" 开始到端口号结束的整个部分
      final pattern = RegExp(
        r'address\s*=\s*\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b\s*,\s*port\s*=\s*\d{2,5}',
        caseSensitive: false,
      );
      
      // 直接替换为空字符串
      String filtered = errorMessage.replaceAll(pattern, '');
      
      // 清理可能留下的多余逗号和空格
      filtered = filtered.replaceAll(RegExp(r',\s*,'), ',');
      filtered = filtered.replaceAll(RegExp(r',\s*$'), ''); // 去掉末尾的逗号
      filtered = filtered.replaceAll(RegExp(r'\s+'), ' ').trim();
      
      return filtered;
  }

  // 获取剩余次数（假设接口为 /api/quota）
  Future<void> _fetchQuota() async {
    setState(() {
      loadingQuota = true;
      errorMessage = '';
    });
    try {
      final client = HttpClient();
      // 请将 IP 改为你的实际服务器 IP
      final request = await client.getUrl(Uri.parse('http://43.138.243.151:8888/api/quota'));
      final response = await request.close();
      if (response.statusCode == 200) {
        final stringData = await response.transform(utf8.decoder).join();
        final Map<String, dynamic> data = jsonDecode(stringData);
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
      client.close();
    } catch (e) {
      setState(() {
        errorMessage = _filterSensitiveInfo('网络错误: $e');
        loadingQuota = false;
      });
    }
  }

  

  // 获取数据（原 fetchData）
  Future<void> _fetchData() async {
    setState(() {
      _resetState();
      loading = true;
      buttonText = '...';
      statusText = 'Fetching data...';
      statusColor = Colors.yellow.shade700;
      errorMessage = '';
    });

    try {
      final client = HttpClient();
      // 请将 IP 改为你的实际服务器 IP
      final request = await client.getUrl(Uri.parse('http://43.138.243.151:8888/api/hello/'));
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

        // 成功获取后重新刷新剩余次数（因为服务器会扣减）
        _fetchQuota();

        _startPlay();
      } else {
        setState(() {
          errorMessage = _filterSensitiveInfo('请求失败: ${response.statusCode}');
          buttonText = 'Retry';
          loading = false;
        });
      }
      client.close();
    } catch (e) {
      setState(() {
        errorMessage = _filterSensitiveInfo('错误: $e');
        buttonText = 'Retry';
        loading = false;
      });
    }
  }

  void _onButtonPressed() {
    if (loading) return;
    if (phase == 3 || buttonText == 'Replay' || buttonText == 'Retry') {
      _resetState();
    }
    _fetchData();
  }

  @override
  Widget build(BuildContext context) {
    // 获取屏幕宽度用于自适应按钮宽度
    double screenWidth = MediaQuery.of(context).size.width;
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(15.0),
        child: Column(
          children: [
            const Text(
              '双色球-采用AI大模型',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
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

            // 播放按钮（自适应居中）
            Center(
              child: SizedBox(
                width: screenWidth * 0.6, // 按钮宽度为屏幕宽度的60%
                child: ElevatedButton(
                  onPressed: loading ? null : _onButtonPressed,
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(double.infinity, 50),
                    backgroundColor: loading
                        ? Colors.grey
                        : (buttonText == 'Replay'
                            ? const Color(0xFF6633CC)
                            : const Color(0xFF3399CC)),
                    foregroundColor: Colors.white,
                    textStyle: const TextStyle(fontSize: 30),
                  ),
                  child: Text(buttonText),
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