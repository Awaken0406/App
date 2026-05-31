import 'dart:convert';
import 'dart:typed_data';

class Op {
  static const int reqQuota = 0x01;
  static const int respQuota = 0x02;
  static const int reqDraw = 0x03;
  static const int respDraw = 0x04;
  static const int ping = 0x10;
  static const int pong = 0x11;
  static const int err = 0x7F;

  static String name(int op) {
    switch (op) {
      case reqQuota:
        return 'REQ_QUOTA';
      case respQuota:
        return 'RESP_QUOTA';
      case reqDraw:
        return 'REQ_DRAW';
      case respDraw:
        return 'RESP_DRAW';
      case ping:
        return 'PING';
      case pong:
        return 'PONG';
      case err:
        return 'ERR';
      default:
        return 'OP_0x${op.toRadixString(16).padLeft(2, '0')}';
    }
  }
}

class Frame {
  final int op;
  final int seq;
  final Map<String, dynamic> payload;

  const Frame(this.op, this.seq, this.payload);

  @override
  String toString() => 'Frame(${Op.name(op)}, seq=$seq, payload=$payload)';
}

class ProtocolException implements Exception {
  final String message;
  ProtocolException(this.message);
  @override
  String toString() => 'ProtocolException: $message';
}

const int _magic0 = 0x53;
const int _magic1 = 0x47;
const int _version = 0x01;
const int _headerLen = 12;
const int _maxPayload = 64 * 1024;

Uint8List encodeFrame(Frame frame) {
  final body = utf8.encode(jsonEncode(frame.payload));
  if (body.length > _maxPayload) {
    throw ProtocolException('payload too large: ${body.length}');
  }
  final buf = Uint8List(_headerLen + body.length);
  final bd = ByteData.sublistView(buf);
  bd.setUint8(0, _magic0);
  bd.setUint8(1, _magic1);
  bd.setUint8(2, _version);
  bd.setUint8(3, frame.op & 0xFF);
  bd.setUint32(4, frame.seq, Endian.big);
  bd.setUint32(8, body.length, Endian.big);
  buf.setRange(_headerLen, _headerLen + body.length, body);
  return buf;
}

class FrameDecoder {
  final BytesBuilder _buf = BytesBuilder(copy: false);

  List<Frame> feed(List<int> chunk) {
    _buf.add(chunk);
    final out = <Frame>[];
    while (true) {
      final bytes = _buf.toBytes();
      if (bytes.length < _headerLen) {
        _restore(bytes);
        break;
      }
      if (bytes[0] != _magic0 || bytes[1] != _magic1) {
        throw ProtocolException(
          'bad magic: 0x${bytes[0].toRadixString(16)} 0x${bytes[1].toRadixString(16)}',
        );
      }
      final ver = bytes[2];
      if (ver != _version) {
        throw ProtocolException('unsupported version: $ver');
      }
      final op = bytes[3];
      final bd = ByteData.sublistView(bytes, 0, _headerLen);
      final seq = bd.getUint32(4, Endian.big);
      final length = bd.getUint32(8, Endian.big);
      if (length > _maxPayload) {
        throw ProtocolException('payload too large: $length');
      }
      if (bytes.length < _headerLen + length) {
        _restore(bytes);
        break;
      }
      Map<String, dynamic> payload;
      if (length == 0) {
        payload = const <String, dynamic>{};
      } else {
        final raw = utf8.decode(bytes.sublist(_headerLen, _headerLen + length));
        final decoded = jsonDecode(raw);
        if (decoded is Map<String, dynamic>) {
          payload = decoded;
        } else {
          throw ProtocolException('payload is not a json object');
        }
      }
      out.add(Frame(op, seq, payload));
      final rest = bytes.sublist(_headerLen + length);
      _buf.clear();
      if (rest.isNotEmpty) _buf.add(rest);
    }
    return out;
  }

  void _restore(Uint8List bytes) {
    _buf.clear();
    _buf.add(bytes);
  }
}
