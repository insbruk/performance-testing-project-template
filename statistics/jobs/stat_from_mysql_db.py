import os
import csv
import json
import mysql.connector
from datetime import datetime
from datetime import timedelta
from settings import perf_test_results_dir


dt_format = '%Y-%m-%dT%H:%M:%S'
dt_test_start = datetime.strptime('2020-01-13T16:40:39', dt_format)  # UTC
test_results_dir = f'{perf_test_results_dir}/2020-01-13_Run1650'
if not os.path.exists(test_results_dir):
    os.makedirs(test_results_dir)
os.chdir(test_results_dir)
if not os.path.exists('failed'):
    os.mkdir('failed')
dt_test_end = dt_test_start + timedelta(days=1)
test_start = dt_test_start.strftime(dt_format)
test_end = dt_test_end.strftime(dt_format)
print(f'Searching from {test_start} to {test_end}')
csv_filename = f'app_stat_db_{test_start.split(":")[0]}_-_{test_end.split(":")[0]}.csv'

db = mysql.connector.connect(
    host="host",
    user="user",
    passwd="password"
)
mycursor = db.cursor()


with open(csv_filename, 'w', newline='') as csv_file_obj:
    db_table_cols = ['process_id', 'status', 'creation_date', 'last_update_date']
    csv_cols = db_table_cols + ['total_time_sec']
    csv_writer = csv.DictWriter(csv_file_obj, fieldnames=csv_cols)
    csv_writer.writeheader()

    mycursor.execute(f'''
        SELECT *
        FROM app.job
        where creation_date >= '{test_start}' and last_update_date <= '{test_end}';
    ''')
    jobs = mycursor.fetchall()

    jobs_total = len(jobs)
    jobs_done_list = [job for job in jobs if job[5] == 'done']
    jobs_done_total = len(jobs_done_list)
    jobs_failed_list = [job for job in jobs if job[5] != 'done']
    jobs_failed_total = len(jobs_failed_list)

    for job in jobs_done_list:
        process_id = job[6]
        status = job[5]
        creation_date = job[1]
        last_update_date = job[2]
        csv_writer.writerow(
            {
                'process_id': process_id,
                'status': status,
                'creation_date': creation_date,
                'last_update_date': last_update_date,
                'total_time_sec': last_update_date - creation_date,
            }
        )
    for job in jobs_failed_list:
        process_id = job[6]
        status = job[5]
        request = job[4]
        progress = job[3]
        last_update_date = job[2]
        creation_date = job[1]
        csv_writer.writerow(
            {
                'process_id': process_id,
                'status': status,
                'creation_date': creation_date,
                'last_update_date': last_update_date,
                'total_time_sec': last_update_date - creation_date,
            }
        )
        with open(f'./failed/{process_id}_status_{status}.json', 'w', newline='') as f:  # status
            json.dump(status, f, indent=4)
        with open(f'./failed/{process_id}_request.json', 'w', newline='') as f:  # request payload
            request = json.loads(request)
            json.dump(request, f, indent=4, sort_keys=True)
        with open(f'./failed/{process_id}_progress.json', 'w', newline='') as f:  # progress log
            progress = json.loads(progress)
            json.dump(progress, f, indent=4)

    csv_file_obj.write(f'\n')
    csv_file_obj.write(f'{test_start} - {test_end}, Summary\n')
    csv_file_obj.write(f'Jobs All: ,{jobs_total}\n')
    csv_file_obj.write(f'Jobs Done: ,{jobs_done_total}\n')
    csv_file_obj.write(f'Jobs Failed: ,{jobs_failed_total}\n')
    csv_file_obj.write(f'\n')

mycursor.close()
