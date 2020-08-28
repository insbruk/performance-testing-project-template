import os
import re
import csv
import json
import copy
import numpy
import mysql.connector
from datetime import datetime, timedelta
from .course_setup_steps import steps


test_results_dir = '.'
if not os.path.exists(test_results_dir):
    os.makedirs(test_results_dir)
os.chdir(test_results_dir)
logs = [log for log in os.listdir(test_results_dir) if log.endswith('.log')]
db = mysql.connector.connect(
    host="host",
    user="test",
    passwd="test"
)
mycursor = db.cursor()
logs_datetime_format = '%Y-%m-%dT%H:%M:%S,%fZ'
db_datetime_format = '%Y-%m-%d %H:%M:%S'
logs_test_start = datetime.strptime('2020-01-13T16:40:39,000Z', logs_datetime_format)  # UTC time
db_test_start = logs_test_start.strftime(db_datetime_format)
logs_test_end = logs_test_start + timedelta(days=1)
db_test_end = logs_test_end.strftime(db_datetime_format)
csv_filename = f'job_analysis_{db_test_start.split(" ")[0]}_-_{db_test_end.split(" ")[0]}.csv'
logs_datetime_pattern = re.compile('\\[([a-z0-9-:T,Z]+)\\]')
logs_process_pattern = re.compile('\\[processId::([a-z0-9-]+)\\]')
print(f'Analysis: {csv_filename} ...')

mycursor.execute(
    f'''
        SELECT process_id
        FROM app.job
        where creation_date >= '{db_test_start}' and creation_date <= '{db_test_end}' and status = 'done';
    '''
)
jobs_done = mycursor.fetchall()
jobs_done = [job[0] for job in jobs_done]
# jobs_done = [
#     '38514aa9-37e9-4401-9cf8-c9e249bb9df9',
#     '1dbe2f2a-b5ae-4d07-9833-bc757b7203ba',
#     'ecefbd71-c334-4875-aba0-7d81300f2521',
#     '6d2a3d9f-7d68-4f03-92c6-b1abf460a26b',
#     'f81d0161-1133-4c2c-95f9-7f159c168c0e',
#     'b8474745-7449-4a46-b093-eb64f6c757ca',
#     'c62346fb-331e-4994-a1df-c03479a8bbee',
# ]
jobs = {pid: copy.deepcopy(steps) for pid in jobs_done}
steps = [step for step in steps if step['included']]

for pid in jobs:
    for log in logs:
        with open(log, 'r') as logfile:
            for line in logfile:
                if line.find(pid) > -1:
                    for step_id in range(len(jobs[pid])):
                        if all(s in line for s in jobs[pid][step_id]['start']):
                            dt = ''
                            dt = re.search(logs_datetime_pattern, line).group(1)
                            dt = datetime.strptime(dt, logs_datetime_format)
                            ts = dt.timestamp()
                            jobs[pid][step_id]['start_ts'] = round(ts, 3)
                        if all(s in line for s in jobs[pid][step_id]['end']):
                            dt = ''
                            dt = re.search(logs_datetime_pattern, line).group(1)
                            dt = datetime.strptime(dt, logs_datetime_format)
                            ts = dt.timestamp()
                            jobs[pid][step_id]['end_ts'] = round(ts, 3)
    print('\n', pid, jobs[pid])

for job in jobs:
    for s in range(len(jobs[job])):
        jobs[job][s]['time'] = jobs[job][s]['end_ts'] - jobs[job][s]['start_ts']
        jobs[job][s]['time'] = round(jobs[job][s]['time'], 3)

for step in range(len(steps)):
    for job in jobs:
        steps[step]['stat'].append(jobs[job][step]['time'])

with open(csv_filename, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['process_id', ] + [step['name'].lower().replace(' ', '_') for step in steps])
    for pid in jobs:
        csv_row = [pid, ]
        for step_id in range(len(jobs[pid])):
            job_step_start_ts = jobs[pid][step_id]["start_ts"]
            job_step_end_ts = jobs[pid][step_id]["end_ts"]
            csv_row.append(f'={job_step_end_ts}-{job_step_start_ts}')
        csv_writer.writerow(csv_row)

    metrics = ['MIN', 'p25', 'p50', 'p90', 'p95', 'p99', 'MAX']
    csv_writer.writerow(['', ])
    csv_writer.writerow(['', ] + [step['name'].lower().replace(' ', '_') for step in jobs[pid]])
    for metric in metrics:
        csv_row = [metric, ]
        for s in range(len(jobs[pid])):
            step_stat = steps[s]['stat']
            if 'MIN' in metric:
                val = round(min(step_stat), 3)
                csv_row.append(val)
            if 'p' in metric:
                pct = int(metric.split('p')[1])
                val = round(numpy.percentile(step_stat, pct), 3)
                csv_row.append(val)
            if 'MAX' in metric:
                val = round(max(step_stat), 3)
                csv_row.append(val)
        csv_writer.writerow(csv_row)
