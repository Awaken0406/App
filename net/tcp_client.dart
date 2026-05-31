import 'dart:async';
import 'dart:io';

import 'protocol.dart';

enum ConnState { disconnected, connecting, connected }

class NotConnectedException implements Exception {
  @override
  String toString() => 'NotConnectedException: socket not connected';
}

class ServerErrorException implements Exception {
  final int code;
  final String message;
  ServerErrorException(this.code, this.message);
  @override
  String toString() => 'ServerError($code): $message';
}

class TcpClient {
  TcpClient({
    required this.host,
    required this.port,
    this.connectTimeout = const Duration(seconds: 5),
    this.requestTimeout = const Duration(seconds: 10),
    this.heartbeatInterval = const Duration(seconds: 30),
    this.idleTimeout = const Duration(seconds: 60),
  });

  final String host;
  final int port;
  final Duration connectTimeout;
  final Duration requestTimeout;
  final Duration heartbeatInterval;
  final Duration idleTimeout;

  final _stateCtrl = StreamController<ConnState>.broadcast();
  Stream<ConnState> get state => _stateCtrl.stream;
  ConnState _state = ConnState.disconnected;
  ConnState get currentState => _state;

  Socket? _socket;
  FrameDecoder _decoder = FrameDecoder();
  final _pending = <int, Completer<Frame>>{};
  int _seq = 0;
  Timer? _heartbeatTimer;
  Timer? _idleTimer;
  DateTime _lastFrameAt = DateTime.now();

  bool _running = false;
  int _backoffMs = 1000;
  static const int _backoffMaxMs = 30000;

  Future<void> start() async {
    if (_running) return;
    _running = true;
    unawaited(_runLoop());
  }

  Future<void> stop() async {
    _running = false;
    await _teardown();
    await _stateCtrl.close();
  }

  Future<Frame> request(int op, [Map<String, dynamic>? payload]) async {
    final socket = _socket;
    if (_state != ConnState.connected || socket == null) {
      throw NotConnectedException();
    }
    final seq = _nextSeq();
    final frame = Frame(op, seq, payload ?? const <String, dynamic>{});
    final completer = Completer<Frame>();
    _pending[seq] = completer;
    try {
      socket.add(encodeFrame(frame));
      await socket.flush();
    } catch (e) {
      _pending.remove(seq);
      rethrow;
    }
    try {
      final resp = await completer.future.timeout(requestTimeout);
      if (resp.op == Op.err) {
        final code = (resp.payload['code'] as num?)?.toInt() ?? -1;
        final msg = resp.payload['message']?.toString() ?? 'unknown error';
        throw ServerErrorException(code, msg);
      }
      return resp;
    } finally {
      _pending.remove(seq);
    }
  }

  int _nextSeq() {
    _seq = (_seq + 1) & 0xFFFFFFFF;
    if (_seq == 0) _seq = 1;
    return _seq;
  }

  void _setState(ConnState s) {
    if (_state == s) return;
    _state = s;
    if (!_stateCtrl.isClosed) _stateCtrl.add(s);
  }

  Future<void> _runLoop() async {
    while (_running) {
      _setState(ConnState.connecting);
      try {
        final socket = await Socket.connect(host, port, timeout: connectTimeout);
        socket.setOption(SocketOption.tcpNoDelay, true);
        _socket = socket;
        _decoder = FrameDecoder();
        _lastFrameAt = DateTime.now();
        _backoffMs = 1000;
        _setState(ConnState.connected);
        _startHeartbeat();
        _startIdleWatch();

        final done = Completer<void>();
        socket.listen(
          (data) {
            try {
              _lastFrameAt = DateTime.now();
              final frames = _decoder.feed(data);
              for (final f in frames) {
                _dispatch(f);
              }
            } catch (e) {
              if (!done.isCompleted) done.completeError(e);
              socket.destroy();
            }
          },
          onError: (e) {
            if (!done.isCompleted) done.completeError(e);
          },
          onDone: () {
            if (!done.isCompleted) done.complete();
          },
          cancelOnError: true,
        );
        await done.future;
      } catch (_) {
        // swallow; will reconnect
      }
      await _teardown();
      _setState(ConnState.disconnected);
      if (!_running) break;
      await Future.delayed(Duration(milliseconds: _backoffMs));
      _backoffMs = (_backoffMs * 2).clamp(1000, _backoffMaxMs);
    }
  }

  void _dispatch(Frame f) {
    if (f.op == Op.pong) return;
    final c = _pending.remove(f.seq);
    if (c != null && !c.isCompleted) {
      c.complete(f);
    }
  }

  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(heartbeatInterval, (_) {
      final s = _socket;
      if (s == null) return;
      try {
        s.add(encodeFrame(Frame(Op.ping, _nextSeq(), const <String, dynamic>{})));
      } catch (_) {
        s.destroy();
      }
    });
  }

  void _startIdleWatch() {
    _idleTimer?.cancel();
    _idleTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      if (DateTime.now().difference(_lastFrameAt) > idleTimeout) {
        _socket?.destroy();
      }
    });
  }

  Future<void> _teardown() async {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = null;
    _idleTimer?.cancel();
    _idleTimer = null;
    final s = _socket;
    _socket = null;
    if (s != null) {
      try {
        await s.close();
      } catch (_) {}
      s.destroy();
    }
    for (final c in _pending.values) {
      if (!c.isCompleted) c.completeError(NotConnectedException());
    }
    _pending.clear();
  }
}
