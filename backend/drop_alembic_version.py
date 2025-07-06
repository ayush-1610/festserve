import psycopg2

conn = psycopg2.connect(
    dbname="festserve", user="festserve", password="festserve", host="db", port=5432
)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS alembic_version;")
conn.commit()
cur.close()
conn.close()
print("Dropped alembic_version table.")
