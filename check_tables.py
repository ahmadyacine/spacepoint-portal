import psycopg2

conn = psycopg2.connect('postgresql://postgres:Ahmad213%23@localhost:5432/portal')
curs = conn.cursor()
curs.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
rows = curs.fetchall()
for row in rows:
    print(row[0])
