import os
import re
import base64
import shutil
import zipfile
import requests
from datetime import datetime, timedelta
from contextlib import contextmanager


@contextmanager
def open_work_dir(path):
    # helper for changing directories
    cur_work_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cur_work_dir)


def base64_encode_credentials(username='', password=''):
    return base64.b64encode(f"{username}:{password}".encode("unicode_escape")).decode("utf-8")


def archive_lr_test_results(tests_dir='', archive_dir=''):
    os.chdir(tests_dir)
    for folder in os.listdir():
        if datetime.strptime(folder.split('_')[0], '%Y-%m-%d') < datetime.today() - timedelta(days=90):
            print(folder)
            with zipfile.ZipFile(f'{archive_dir}/{folder}.zip', "w", zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        zip_file.write(os.path.join(root, file))
            shutil.rmtree(folder, ignore_errors=True)


def clear_console_output():
    os.system('cls')


def download_file(url, dst, fname):
    with requests.Session() as session:
        print(f'{url} is downloading')
        request = session.get(url)
        print(request)
        if request.ok:
            print(f'{url} was downloaded')
            content = request.content
            with open_work_dir(dst):
                with open(fname, 'wb') as f:
                    f.write(content)


def zip_dir(dir_name):
    zip_name = f'{dir_name}.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_f:
        with open_work_dir(dir_name):
            for root, dirs, files in os.walk('.'):
                for file in files:
                    zip_f.write(os.path.join(root, file))
    return zip_name


def unzip(zip_name, dst=None):
    dir_name = zip_name.split('.')[0]
    with zipfile.ZipFile(zip_name) as zf:
        zf.extractall(path=dst)
    return dir_name


def clear(path):
    files_pattern = re.compile(
        '(?:.+\.bak)|'
        '(?:.+\.tmp)|'
        '(?:.+\.log)|'
        '(?:.+\.idx)|'
        '(?:.+\.har)|'
        '(?:.+\.shunra)|'
        '(?:.+\.c.pickle)|'
        '(?:.+\.prm\.bak)|'
        '(?:.+\.sdf)|'
        '(?:.+\.ci)|'
        '(?:output\.txt)|'
        '(?:options\.txt)|'
        '(?:mdrv_cmd\.txt)|'
        '(?:serTasks\.xml)|'
        '(?:Bookmarks\.xml)|'
        '(?:Breakpoints\.xml)|'
        '(?:Watches\.xml)|'
        '(?:UserTasks\.xml)|'
        '(?:ReplaySummaryReport\.xml)|'
        '(?:CompilerLogMetadata\.xml)|'
        '(?:ScriptUploadMetadata\.xml)|'
        '(?:pre_cci\.c)|'
        '(?:combined_.+\.c)|'
        '(?:lrw_custom_body\.h)|'
        '(?:TransactionsData\.db)|'
        '(?:OutputColoringDatabase\.json)'
    )

    dirs_patterns = re.compile('(?:DfeConfig)|(?:result[0-9])|(?:^data$)')
    with open_work_dir(path):
        print(f'Clear "{path}" ...')
        for item in os.listdir():
            if os.path.isdir(item):
                if dirs_patterns.match(item):
                    for root, dirs, files in os.walk(item, topdown=False):
                        for f in files:
                            os.remove(os.path.join(root, f))
                        for d in dirs:
                            os.rmdir(os.path.join(root, d))
                    os.rmdir(item)
            if files_pattern.match(item):
                os.remove(item)