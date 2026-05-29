import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'net/protocol.dart';
import 'net/tcp_client.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
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
  static const String serverHost = '43.138.243.151';
  static const int serverPort = 9527;
  static const String buttonText = '来财';

  List<int> redArray = [0, 0, 0, 0, 0, 0];
  List<int> blueArray = [0];

  bool playing = false;
  int redIndex = 0;
  int blueIndex = 0;
  int phase = 0; // 0:未播放/完成, 1:红区播放中, 2:蓝区播放中, 3:完成

  List<bool> redVisible = [];
  List<bool> blueVisible = [];

  String descriptionText = '双色球-采用大模型';
  String statusText = 'Start';
  Color statusColor = Colors.grey.shade400;
  String progressText = '';

  bool loading = false;
  bool _isCompleted = false;
  bool _isError = false;

  String errorMessage = '';
  int remainingQuota = 0;
  bool loadingQuota = true;
  ConnState _connState = ConnState.disconnected;

  Timer? _timer;
  late final TcpClient _client;
  StreamSubscription<ConnState>? _stateSub;
  bool _initialQuotaFetched = false;

  @override
  void initState() {
    super.initState();
    _initVisibility();
    _client = TcpClient(host: serverHost, port: serverPort);
    _stateSub = _client.state.listen(_onConnState);
    _client.start();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _stateSub?.cancel();
    _client.stop();
    super.dispose();
  }

  void _onConnState(ConnState s) {
    if (!mounted) return;
    setState(() {
      _connState = s;
    });
    if (s == ConnState.connected && !_initialQuotaFetched) {
      _initialQuotaFetched = true;
      _fetchQuota();
    }
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
          progressText = '${redIndex + 1}/${redArray.length} | $blueIndex/${blueArray.length}';
        });
        redIndex++;
        if (redIndex >= redArray.length) {
          setState(() {
            phase = 2;
            statusText = '...';
            statusColor = const Color(0xFF9999FF);
          });
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

  void _finishPlay() {
    _timer?.cancel();
    setState(() {
      playing = false;
      phase = 3;
      loading = false;
      statusText = 'Done';
      statusColor = const Color(0xFFCC88CC);
      progressText = '${redArray.length}/${redArray.length} | ${blueArray.length}/${blueArray.length}';
      _isCompleted = true;
    });
  }

  String _humanizeError(Object e) {
    if (e is NotConnectedException) return '未连接，正在重连...';
    if (e is TimeoutException) return '请求超时';
    if (e is ServerErrorException) return e.message;
    final s = e.toString();
    return s.replaceAll(RegExp(r'(\d{1,3}\.){3}\d{1,3}(:\d{2,5})?'), '').trim();
  }

  Future<void> _fetchQuota() async {
    if (!mounted) return;
    setState(() {
      loadingQuota = true;
      errorMessage = '';
    });

    try {
      final f = await _client.request(Op.reqQuota);
      if (!mounted) return;
      setState(() {
        if (f.payload.containsKey('description')) {
          descriptionText = f.payload['description'].toString();
        }
        remainingQuota = (f.payload['remaining'] as num?)?.toInt() ?? 0;
        loadingQuota = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        errorMessage = _humanizeError(e);
        loadingQuota = false;
      });
    }
  }

  Future<void> _fetchData() async {
    setState(() {
      _resetState();
      loading = true;
      _isCompleted = false;
      _isError = false;
      statusText = 'Fetching data...';
      statusColor = Colors.yellow.shade700;
      errorMessage = '';
    });

    try {
      final f = await _client.request(Op.reqDraw);
      if (!mounted) return;
      final data = f.payload;
      final String redStr = data['red']?.toString() ?? '';
      final String blueStr = data['blue']?.toString() ?? '';
      final List<int> newRed =
          redStr.split(',').map((s) => int.tryParse(s.trim()) ?? 0).toList();
      final List<int> newBlue =
          blueStr.split(',').map((s) => int.tryParse(s.trim()) ?? 0).toList();

      setState(() {
        redArray = newRed;
        blueArray = newBlue;
        _initVisibility();
        statusText = 'Done !!!';
        statusColor = Colors.green;
        loading = false;
        if (data.containsKey('description')) {
          descriptionText = data['description'].toString();
        }
        if (data['remaining'] is num) {
          remainingQuota = (data['remaining'] as num).toInt();
        }
      });

      _startPlay();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        errorMessage = _humanizeError(e);
        loading = false;
        _isError = true;
      });
    }
  }

  void _onButtonPressed() {
    if (loading) return;
    if (_isCompleted || _isError) {
      _resetState();
    }
    _fetchData();
  }

  Color _getButtonColor() {
    if (loading) return Colors.grey;
    if (_isCompleted) return const Color(0xFF6633CC);
    if (_isError) return Colors.red;
    return const Color(0xFF3399CC);
  }

  String _quotaLabel() {
    if (_connState != ConnState.connected) {
      return _connState == ConnState.connecting ? '连接中...' : '未连接';
    }
    if (loadingQuota) return '获取剩余次数中...';
    return '今日剩余次数:$remainingQuota';
  }

  @override
  Widget build(BuildContext context) {
    final double screenWidth = MediaQuery.of(context).size.width;
    final bool buttonEnabled = !loading &&
        _connState == ConnState.connected &&
        remainingQuota > 0;
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/background.jpg'),
            fit: BoxFit.cover,
            opacity: 0.3,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(15.0),
          child: Column(
            children: [
              Text(
                descriptionText,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 10),
              Text(
                _quotaLabel(),
                style: TextStyle(
                  fontSize: 18,
                  color: _connState == ConnState.connected
                      ? (remainingQuota > 0 ? Colors.green : Colors.red)
                      : Colors.orange,
                ),
              ),
              const SizedBox(height: 20),
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
              Text(
                progressText,
                style: const TextStyle(fontSize: 16, color: Color(0xFFCCCCCC)),
              ),
              const SizedBox(height: 20),
              Center(
                child: SizedBox(
                  width: screenWidth * 0.6,
                  child: ElevatedButton(
                    onPressed: buttonEnabled ? _onButtonPressed : null,
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                      backgroundColor: _getButtonColor(),
                      foregroundColor: Colors.white,
                      textStyle: const TextStyle(fontSize: 30),
                    ),
                    child: const Text(buttonText),
                  ),
                ),
              ),
              const SizedBox(height: 10),
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
          final visible = visibleList[index];
          return Container(
            width: 60,
            height: 60,
            margin: const EdgeInsets.symmetric(horizontal: 5),
            decoration: BoxDecoration(shape: BoxShape.circle, color: bgColor),
            child: Center(
              child: AnimatedOpacity(
                opacity: visible ? 1.0 : 0.0,
                duration: const Duration(milliseconds: 500),
                curve: Curves.easeIn,
                child: Text(
                  visible ? '${array[index]}' : '',
                  style: TextStyle(
                    fontSize: 28,
                    color: textColor.withValues(alpha: visible ? 1 : 0),
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
