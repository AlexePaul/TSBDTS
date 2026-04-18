import oracledb

conn = oracledb.connect(
    user="system",
    password="Gigibecali04$$",
    dsn="localhost:1521/FREEPDB1"
)

with conn.cursor() as cur:
    cur.execute("SELECT 'OK' FROM dual")
    print(cur.fetchone()[0])

conn.close()