from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date
import random
import uvicorn
import asyncio
import aiomysql
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import Selenium_Ball  # 你的原始模块

# ==================== 配置 ====================
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'db': 'senge',
    'autocommit': True
}
RATE_LIMIT_PER_DAY = 3  # 每个IP每天最多请求次数

# SSL 证书文件路径（请根据实际路径修改）
SSL_CERTFILE = "/path/to/your/certificate.pem"   # 例如 ./cert.pem
SSL_KEYFILE  = "/path/to/your/private.key"       # 例如 ./key.pem

# ==================== 全局变量 ====================
app = FastAPI(title="Simple API Demo with Rate Limit")
pool = None                # MySQL连接池
ip_cache = {}              # 内存缓存: {ip: (count, today_date)}
cache_lock = asyncio.Lock() # 缓存锁
scheduler = AsyncIOScheduler()

# ==================== 数据库初始化 ====================
async def init_db():
    global pool
    pool = await aiomysql.create_pool(**MYSQL_CONFIG)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS rate_limit (
                    ip VARCHAR(45) PRIMARY KEY,
                    count INT NOT NULL DEFAULT 0,
                    date DATE NOT NULL
                )
            """)
            await conn.commit()

async def close_db():
    if pool:
        pool.close()
        await pool.wait_closed()

# ==================== 清空任务 ====================
async def reset_all_limits():
    """每日零点清空内存缓存和数据库"""
    global ip_cache
    async with cache_lock:
        ip_cache.clear()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM rate_limit")
            await conn.commit()
    print(f"[{datetime.now()}] 已清空所有请求计数")

# ==================== 限流依赖 ====================
async def rate_limit(request: Request):
    client_ip = request.client.host
    today = date.today()

    async with cache_lock:
        # 1. 检查内存缓存
        cached = ip_cache.get(client_ip)
        if cached and cached[1] == today:
            count = cached[0]
        else:
            # 2. 缓存未命中或日期不符，查询数据库
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT count, date FROM rate_limit WHERE ip = %s",
                        (client_ip,)
                    )
                    row = await cur.fetchone()
            if row and row[1] == today:
                count = row[0]
            else:
                # 3. 新IP或新的一天，插入/重置
                count = 0
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "INSERT INTO rate_limit (ip, count, date) VALUES (%s, %s, %s) "
                            "ON DUPLICATE KEY UPDATE count = %s, date = %s",
                            (client_ip, 0, today, 0, today)
                        )
                        await conn.commit()
            # 更新缓存
            ip_cache[client_ip] = (count, today)

    # 4. 判断是否超限
    if count >= RATE_LIMIT_PER_DAY:
        raise HTTPException(status_code=429, detail="请求次数超限，请明天再试")

    # 5. 增加计数（内存中增加，异步写回数据库）
    async with cache_lock:
        ip_cache[client_ip] = (count + 1, today)
        # 触发异步数据库更新（不等待）
        asyncio.create_task(update_db_count(client_ip, count + 1, today))

    # 继续处理请求
    return client_ip  # 可以传递，这里不必须

async def update_db_count(ip: str, new_count: int, today: date):
    """异步将计数写入数据库"""
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE rate_limit SET count = %s WHERE ip = %s AND date = %s",
                    (new_count, ip, today)
                )
                await conn.commit()
    except Exception as e:
        print(f"更新数据库失败 {ip}: {e}")

# ==================== 新增接口：查询剩余次数 ====================
@app.get("/api/quota")
async def get_quota(request: Request):
    """返回当前IP剩余的请求次数（不消耗次数）"""
    client_ip = request.client.host
    today = date.today()

    async with cache_lock:
        # 优先从缓存读取
        cached = ip_cache.get(client_ip)
        if cached and cached[1] == today:
            count = cached[0]
        else:
            # 缓存不存在或日期不符，从数据库查询
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT count, date FROM rate_limit WHERE ip = %s",
                        (client_ip,)
                    )
                    row = await cur.fetchone()
            if row and row[1] == today:
                count = row[0]
            else:
                count = 0  # 从未请求过，剩余次数为 RATE_LIMIT_PER_DAY
            # 更新缓存（只读，不改变计数）
            ip_cache[client_ip] = (count, today)

    remaining = max(0, RATE_LIMIT_PER_DAY - count)
    return {"remaining": remaining,"description":"双色球-采用SENGE AI大模型"}

# ==================== 原始路由（添加依赖） ====================
class EchoResponse(BaseModel):
    received: Dict[str, Any]
    message: str = "Data received"

@app.get("/api/hello", dependencies=[Depends(rate_limit)])
async def hello(name: Optional[str] = "World"):
    outred, outblue = Selenium_Ball.CallRun()
    red = ", ".join(map(str, outred))
    blue = ", ".join(map(str, outblue))
    return {
        "message": f"Hello {name}!",
        "method": "GET",
        "red": red,
        "blue": blue
    }

@app.post("/api/echo", response_model=EchoResponse, dependencies=[Depends(rate_limit)])
async def echo(request: Request):
    data = await request.json()
    return {
        "received": data,
        "message": "Data received"
    }

@app.get("/api/status", dependencies=[Depends(rate_limit)])
@app.post("/api/status", dependencies=[Depends(rate_limit)])
async def status(request: Request):
    body = await request.json() if request.method == "POST" else None
    return {
        "status": "ok",
        "method": request.method,
        "query_params": dict(request.query_params),
        "body": body
    }

# ==================== 生命周期管理 ====================
@app.on_event("startup")
async def startup():
    await init_db()
    # 添加每日零点清空任务
    scheduler.add_job(reset_all_limits, CronTrigger(hour=0, minute=0, second=0))
    scheduler.start()
    print("限流服务已启动，每日零点自动重置")

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()
    await close_db()

# ==================== 启动（HTTPS） ====================
if __name__ == "__main__":
    now = datetime.now()
    random.seed(now.timestamp())
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8888,
        #ssl_keyfile=SSL_KEYFILE,    # 私钥文件路径
        #ssl_certfile=SSL_CERTFILE   # 证书文件路径
    )