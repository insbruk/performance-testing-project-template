import os
import gzip
import shutil
from lib import linux


test_results_dir = '.'
instances = [
    '10.221.237.249',
    '10.221.174.246',
    '10.221.171.129',
    '10.221.233.208',
]
logs = [
    f'app.2020-01-13.log.gz',
    'app.log'
]
if not os.path.exists(test_results_dir):
    os.makedirs(test_results_dir)
os.chdir(test_results_dir)

for instance in instances:
    server = linux.LinuxServer(host=instance)
    server.ftp_connection(
        username='tester',
        password='tester',
    )

    for log in logs:
        server.download_file(
            src=f'/opt/logs/{log}',
            dst=test_results_dir
        )
        if log.endswith('.gz'):
            app = log.split('.')[0]
            date = log.split('.')[1]
            # local_zip_name = f'{app}_{instance}_{date}.log.gz'
            # os.rename(log, local_log_name)
            local_log_name = f'{app}_{instance}_{date}.log'
            with gzip.open(log, 'rb') as f_in:
                with open(local_log_name, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(log)
        if log.endswith('.log'):
            app = log.split('.')[0]
            date = server.execute('date +"%Y-%m-%d"')[0].decode('utf-8').strip()
            local_log_name = f'{app}_{instance}_{date}.log'
            os.rename(log, local_log_name)