"""Reference TCP server for the Flutter Number Area app.

Frame layout (big-endian):
    magic[2]=0x53,0x47 | ver(1) | op(1) | seq(4) | length(4) | payload(length)
payload = UTF-8 JSON object (may be empty when length == 0).

Persistence: per-IP daily request count is stored in MySQL (`rate_limit` table),
mirrored to an in-memory cache. APScheduler resets both at local 00:00:00.

Run:
    python server.py --host 0.0.0.0 --port 9527
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import random
import struct
from dataclasses import dataclass
from datetime import date, datetime

import aiomysql
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import Selenium_Ball
# ==================== 协议常量 ====================
MAGIC0 = 0x53
MAGIC1 = 0x47
VERSION = 0x01
HEADER = struct.Struct(">BBBBII")  # magic0, magic1, ver, op, seq, length
MAX_PAYLOAD = 64 * 1024

OP_REQ_QUOTA = 0x01
OP_RESP_QUOTA = 0x02
OP_REQ_DRAW = 0x03
OP_RESP_DRAW = 0x04
OP_PING = 0x10
OP_PONG = 0x11
OP_ERR = 0x7F

DESCRIPTION = "双色球-采用SENGE大模型"
DEFAULT_DAILY_QUOTA = 3

# ==================== 全局状态 ====================
log = logging.getLogger("tcp_server")
pool: aiomysql.Pool | None = None
ip_cache: dict[str, tuple[int, date]] = {}
cache_lock = asyncio.Lock()
scheduler = AsyncIOScheduler()
DAILY_QUOTA = DEFAULT_DAILY_QUOTA


# ==================== Frame 编解码 ====================
@dataclass
class Frame:
    op: int
    seq: int
    payload: dict


def encode(frame: Frame) -> bytes:
    body = json.dumps(frame.payload, ensure_ascii=False).encode("utf-8")
    if len(body) > MAX_PAYLOAD:
        raise ValueError(f"payload too large: {len(body)}")
    head = HEADER.pack(MAGIC0, MAGIC1, VERSION, frame.op & 0xFF, frame.seq, len(body))
    return head + body


async def read_frame(reader: asyncio.StreamReader) -> Frame:
    head = await reader.readexactly(HEADER.size)
    m0, m1, ver, op, seq, length = HEADER.unpack(head)
    if m0 != MAGIC0 or m1 != MAGIC1:
        raise ValueError(f"bad magic: 0x{m0:02x} 0x{m1:02x}")
    if ver != VERSION:
        raise ValueError(f"unsupported version: {ver}")
    if length > MAX_PAYLOAD:
        raise ValueError(f"payload too large: {length}")
    body = await reader.readexactly(length) if length else b""
    payload = json.loads(body.decode("utf-8")) if body else {}
    if not isinstance(payload, dict):
        raise ValueError("payload is not a json object")
    return Frame(op=op, seq=seq, payload=payload)


# ==================== 数据库 ====================
async def init_db(cfg: dict) -> None:
    global pool
    pool = await aiomysql.create_pool(**cfg)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS rate_limit (
                    ip VARCHAR(45) PRIMARY KEY,
                    count INT NOT NULL DEFAULT 0,
                    date DATE NOT NULL
                )
                """
            )
            await conn.commit()
    log.info("MySQL connected (db=%s)", cfg.get("db"))


async def close_db() -> None:
    global pool
    if pool is not None:
        pool.close()
        await pool.wait_closed()
        pool = None


async def reset_all_limits() -> None:
    """每日零点清空内存缓存与数据库。"""
    async with cache_lock:
        ip_cache.clear()
    if pool is not None:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM rate_limit")
                await conn.commit()
    log.info("daily quota reset done at %s", datetime.now().isoformat(timespec="seconds"))


async def _load_count_from_db(ip: str, today: date) -> int:
    assert pool is not None
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT count, date FROM rate_limit WHERE ip = %s",
                (ip,),
            )
            row = await cur.fetchone()
    if row and row[1] == today:
        return int(row[0])
    return 0


async def _upsert_count(ip: str, count: int, today: date) -> None:
    assert pool is not None
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO rate_limit (ip, count, date) VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE count = %s, date = %s",
                    (ip, count, today, count, today),
                )
                await conn.commit()
    except Exception as e:
        log.warning("db upsert failed for %s: %s", ip, e)


async def get_count(ip: str) -> int:
    """读：返回今天该 IP 已消耗的次数（不消耗）。"""
    today = date.today()
    async with cache_lock:
        cached = ip_cache.get(ip)
        if cached and cached[1] == today:
            return cached[0]
        count = await _load_count_from_db(ip, today)
        ip_cache[ip] = (count, today)
        return count


async def consume_one(ip: str) -> tuple[bool, int]:
    """写：尝试消耗一次。返回 (是否成功, 剩余次数)。"""
    today = date.today()
    async with cache_lock:
        cached = ip_cache.get(ip)
        if cached and cached[1] == today:
            count = cached[0]
        else:
            count = await _load_count_from_db(ip, today)
        if count >= DAILY_QUOTA:
            ip_cache[ip] = (count, today)
            return False, 0
        new_count = count + 1
        ip_cache[ip] = (new_count, today)
        asyncio.create_task(_upsert_count(ip, new_count, today))
        return True, max(0, DAILY_QUOTA - new_count)


# ==================== 业务 ====================
def draw_lottery() -> tuple[list[int], list[int]]:
    red, blue = Selenium_Ball.CallRun()
    return red, blue


async def dispatch(frame: Frame, writer: asyncio.StreamWriter, ip: str) -> None:
    if frame.op == OP_PING:
        writer.write(encode(Frame(OP_PONG, frame.seq, {})))
        await writer.drain()
        return

    if frame.op == OP_REQ_QUOTA:
        used = await get_count(ip)
        remaining = max(0, DAILY_QUOTA - used)
        writer.write(
            encode(
                Frame(
                    OP_RESP_QUOTA,
                    frame.seq,
                    {"description": DESCRIPTION, "remaining": remaining},
                )
            )
        )
        await writer.drain()
        return

    if frame.op == OP_REQ_DRAW:
        ok, remaining = await consume_one(ip)
        if not ok:
            writer.write(
                encode(
                    Frame(OP_ERR, frame.seq, {"code": 429, "message": "今日次数已用完"})
                )
            )
            await writer.drain()
            return
        red, blue = draw_lottery()
        writer.write(
            encode(
                Frame(
                    OP_RESP_DRAW,
                    frame.seq,
                    {
                        "red": ",".join(map(str, red)),
                        "blue": ",".join(map(str, blue)),
                        "remaining": remaining,
                        "description": DESCRIPTION,
                    },
                )
            )
        )
        await writer.drain()
        return

    writer.write(
        encode(
            Frame(
                OP_ERR,
                frame.seq,
                {"code": 400, "message": f"unknown op: 0x{frame.op:02x}"},
            )
        )
    )
    await writer.drain()


# ==================== 连接处理 ====================
async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    peer = writer.get_extra_info("peername")
    ip = peer[0] if peer else "unknown"
    log.info("client connected: %s", peer)
    try:
        while True:
            try:
                frame = await read_frame(reader)
            except asyncio.IncompleteReadError:
                break
            except (ValueError, json.JSONDecodeError) as e:
                log.warning("[%s] bad frame: %s", ip, e)
                break
            await dispatch(frame, writer, ip)
    finally:
        log.info("client disconnected: %s", peer)
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


# ==================== 启动 ====================
async def main_async(host: str, port: int, mysql_cfg: dict) -> None:
    await init_db(mysql_cfg)
    scheduler.add_job(reset_all_limits, CronTrigger(hour=0, minute=0, second=0))
    scheduler.start()
    log.info("scheduler started: daily reset at 00:00:00 (local)")

    server = await asyncio.start_server(handle_client, host=host, port=port)
    addrs = ", ".join(str(s.getsockname()) for s in server.sockets)
    log.info("listening on %s (daily quota=%d)", addrs, DAILY_QUOTA)

    try:
        async with server:
            await server.serve_forever()
    finally:
        scheduler.shutdown(wait=False)
        await close_db()


def main() -> None:
    global DAILY_QUOTA
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9527)
    parser.add_argument("--daily", type=int, default=DEFAULT_DAILY_QUOTA)
    parser.add_argument("--mysql-host", default="localhost")
    parser.add_argument("--mysql-port", type=int, default=3306)
    parser.add_argument("--mysql-user", default="root")
    parser.add_argument("--mysql-password", default="Root@123456")
    parser.add_argument("--mysql-db", default="senge")
    parser.add_argument("--log", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log.upper(), format="%(asctime)s %(levelname)s %(message)s"
    )
    DAILY_QUOTA = args.daily
    random.seed(datetime.now().timestamp())

    mysql_cfg = {
        "host": args.mysql_host,
        "port": args.mysql_port,
        "user": args.mysql_user,
        "password": args.mysql_password,
        "db": args.mysql_db,
        "autocommit": True,
    }
    try:
        asyncio.run(main_async(args.host, args.port, mysql_cfg))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
