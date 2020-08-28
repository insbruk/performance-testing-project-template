import mysql.connector


mysql_perf_db = mysql.connector.connect(
        host='host',
        user="user",
        passwd="password"
)
mysql_prod_db = mysql.connector.connect(
        host='host',
        user="user",
        passwd="password"
)

sql = """
    select TABLE_NAME from 
    INFORMATION_SCHEMA.TABLES 
    where TABLE_TYPE = 'BASE TABLE'
    order by TABLE_NAME asc;
"""

mysql_perf_db_cursor = mysql_perf_db.cursor()
mysql_prod_db_cursor = mysql_prod_db.cursor()

mysql_prod_db_cursor.execute(sql)
tables = mysql_prod_db_cursor.fetchall()
tables = [t[0] for t in tables]
# print(tables)

print('table,rows_in_prod,rows_in_perf')
for t in tables:
    try:
        mysql_perf_db_cursor.execute(f'select count(*) from app.{t};')
    except mysql.connector.errors.ProgrammingError:
        continue
    mysql_prod_db_cursor.execute(f'select count(*) from app.{t};')
    mysql_perf_count = mysql_perf_db_cursor.fetchone()[0]
    mysql_prod_count = mysql_prod_db_cursor.fetchone()[0]
    print(f'{t},{mysql_prod_count},{mysql_perf_count}')


# db.commit()
mysql_perf_db_cursor.close()
mysql_perf_db.close()
mysql_prod_db_cursor.close()
mysql_prod_db.close()