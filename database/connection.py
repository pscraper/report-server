import asyncio
import aiosqlite


# 비동기 데이터베이스 드라이버
# https://www.encode.io/databases/
# https://blog.neonkid.xyz/269
# https://dev.to/arunanshub/async-database-operations-with-sqlmodel-c2o
# https://hides.kr/1101 

DB_CONN_URL = "sqlite+aiosqlite:///report-server.db"


pool = aiosqlite.connect(DB_CONN_URL)
