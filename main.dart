import 'package:flutter/material.dart';
//import 'package:http/http.dart' as http;
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
  // 初始数组（与 Kivy 版本一致）
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

  // 定时器
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _initVisibility();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  // 根据当前数组初始化可见性列表
  void _initVisibility() {
    redVisible = List.generate(redArray.length, (_) => false);
    blueVisible = List.generate(blueArray.length, (_) => false);
  }

  // 重置所有状态（对应 clickBtn）
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
    });
  }

  // 开始播放（对应 start_play）
  void _startPlay() {
    _timer?.cancel(); // 清除旧定时器
    setState(() {
      playing = true;
      phase = 1; // 红区播放
      redIndex = 0;
      blueIndex = 0;
      buttonText = '...';
    });
    // 每秒显示一个数字
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      _showNextNumber();
    });
  }

  // 显示下一个数字（对应 show_next_number）
  void _showNextNumber() {
    if (!playing) return;

    if (phase == 1) {
      // 红区播放
      if (redIndex < redArray.length) {
        setState(() {
          redVisible[redIndex] = true; // 触发淡入动画
          statusText = '${redIndex + 1} number: ${redArray[redIndex]}...';
          statusColor = const Color(0xFFFF9999); // 浅红
          progressText =
              '${redIndex + 1}/${redArray.length} | ${blueIndex}/${blueArray.length}';
        });
        redIndex++;
        // 红区播放完毕，切换到蓝区
        if (redIndex >= redArray.length) {
          setState(() {
            phase = 2;
            statusText = '...';
            statusColor = const Color(0xFF9999FF); // 浅蓝
          });
          // 红区全部数字闪烁一次（简单模拟：短暂变色后恢复）
          _flashRed();
        }
      }
    } else if (phase == 2) {
      // 蓝区播放
      if (blueIndex < blueArray.length) {
        setState(() {
          blueVisible[blueIndex] = true;
          statusText = '... ${blueIndex + 1} ...: ${blueArray[blueIndex]}';
          progressText =
              '...: ${redArray.length}/${redArray.length} | ...: ${blueIndex + 1}/${blueArray.length}';
        });
        blueIndex++;
        if (blueIndex >= blueArray.length) {
          _finishPlay();
        }
      }
    }
  }

  // 红区播放完成时的闪烁（对应原代码中的闪烁动画）
  void _flashRed() {
    // 简单实现：将所有红区数字颜色变亮一次，再恢复
    Future.delayed(const Duration(milliseconds: 100), () {
      setState(() {}); // 触发 rebuild，实际颜色由 widget 自身控制
    });
  }

  // 播放完成（对应 finish_play）
  void _finishPlay() {
    _timer?.cancel();
    setState(() {
      playing = false;
      phase = 3;
      buttonText = 'Replay';
      loading = false;
      statusText = 'Done';
      statusColor = const Color(0xFFCC88CC); // 紫色
      progressText =
          '${redArray.length}/${redArray.length} | ${blueArray.length}/${blueArray.length}';
    });
    // 蓝区闪烁
    _flashBlue();
  }

  void _flashBlue() {
    Future.delayed(const Duration(milliseconds: 100), () {
      setState(() {});
    });
  }

  // 获取数据（对应 fetch_data）
  Future<void> _fetchData() async {
    setState(() {
      _resetState(); // 先重置
      loading = true;
      buttonText = '...';
      statusText = 'Fetching data...';
      statusColor = Colors.yellow.shade700;
    });

    try {
      // 随机等待 3~8 秒（原代码有 random wait，但被注释，这里保留注释）
      // await Future.delayed(Duration(seconds: Random().nextInt(6) + 3));

      final client = HttpClient();
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
          _initVisibility(); // 重新初始化可见性
          statusText = 'Done !!!';
          statusColor = Colors.green;
          loading = false;
        });

        // 自动开始播放
        _startPlay();
      } else {
        setState(() {
          statusText = 'Request fail: ${response.statusCode}';
          statusColor = Colors.red;
          buttonText = 'Retry';
          loading = false;
        });
      }
    } catch (e) {
      setState(() {
        statusText = 'Error: $e';
        statusColor = Colors.red;
        buttonText = 'Retry';
        loading = false;
      });
    }
  }

  // 按钮点击处理
  void _onButtonPressed() {
    if (loading) return;
    if (phase == 3 || buttonText == 'Replay' || buttonText == 'Retry') {
      _resetState();
    }
    _fetchData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(15.0),
        child: Column(
          children: [
            // 标题
            const Text(
              'Number Area',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 20),

            // 红区区域
            _buildHeaderRow(
              title: 'red',
              titleColor: const Color(0xFFFF6666),
              child: _buildNumberRow(
                array: redArray,
                visibleList: redVisible,
                bgColor: const Color(0xFF6B2D2D), // 深红背景
                textColor: const Color(0xFFFFCCCC),
              ),
            ),

            // 蓝区区域
            _buildHeaderRow(
              title: 'blue',
              titleColor: const Color(0xFF6666FF),
              child: _buildNumberRow(
                array: blueArray,
                visibleList: blueVisible,
                bgColor: const Color(0xFF26264D), // 深蓝背景
                textColor: const Color(0xFFCCCCFF),
              ),
            ),

            const SizedBox(height: 10),

            // 状态标签（原 status_label，实际布局中被注释，此处保留但可以隐藏）
            // 为了与原代码对应，我们将其放在这里但不显示，如需显示可取消注释
            // Container(
            //   alignment: Alignment.center,
            //   child: Text(
            //     statusText,
            //     style: TextStyle(fontSize: 20, color: statusColor),
            //   ),
            // ),

            // 播放按钮（居中）
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 200),
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

            const SizedBox(height: 10),

            // 进度标签
            Text(
              progressText,
              style: const TextStyle(fontSize: 16, color: Color(0xFFCCCCCC)),
            ),
          ],
        ),
      ),
    );
  }

  // 构建标题行（红/蓝 标题 + 数字区域）
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
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w500,
                color: titleColor,
              ),
            ),
          ),
          Expanded(child: child),
        ],
      ),
    );
  }

  // 构建一行数字圆圈
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
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: bgColor,
            ),
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