import csv
import mysql.connector


reg_max_per_day = 'reg_max_per_day.csv'
regs_per_day = 'regs_per_day.csv'
registrations = 'registrations.csv'
database_mysql = mysql.connector.connect(
        host='host',
        user='app',
        passwd='password'
)
mysql_db_cursor = database_mysql.cursor()

sql = '''
    SELECT DATE_FORMAT(created_date_time, "%Y-%m-%d") reg_date, count(*) reg_count
    FROM app.user_login
    where created_date_time > '2018-12-21'
    group by reg_date
    order by reg_date;
'''
mysql_db_cursor.execute(sql)
rows = mysql_db_cursor.fetchall()
with open(regs_per_day, 'w', newline='') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['date', 'regs'])
    csv_writer.writerows(rows)

sql = '''
    SELECT DATE_FORMAT(created_date_time, "%Y-%m-%d") reg_date, count(*) reg_count
    FROM app.user_login
    where created_date_time > '2018-12-21'
    group by reg_date
    order by reg_count desc
    limit 3;
'''
mysql_db_cursor.execute(sql)
rows = mysql_db_cursor.fetchall()
with open(reg_max_per_day, 'w', newline='') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['date', 'regs'])
    csv_writer.writerows(rows)

sql = '''
    SELECT created_date_time
    FROM app.user_login
    where created_date_time > '2018-12-21'
    order by created_date_time;
'''
mysql_db_cursor.execute(sql)
rows = mysql_db_cursor.fetchall()
with open(registrations, 'w', newline='') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['date'])
    csv_writer.writerows(rows)

mysql_db_cursor.close()
database_mysql.close()
