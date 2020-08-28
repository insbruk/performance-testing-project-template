
import re
from datetime import datetime

session_log = 'uni_session.log'
sessions_csv = 'uni_session.csv'

patterns = {
    # 'waiter': re.compile('Waiter=\s+?(\d+?)\s?;?'),
    # 'local_no': re.compile('LOCAL=NO:(\d+?)\s?;?'),
    # 'uni_active': re.compile('UNI\(active\):\s?(\d+);'),
    'student': re.compile('student sessions:(\d+);'),
    'instructor': re.compile('instructor sessions:(\d+);'),
    'assistant': re.compile('assistant sessions:(\d+);'),
    'admin': re.compile('admin sessions:(\d+);'),
    # 'mem_free': re.compile('MEMfree\(GB\): (\d+)\s?;?'),
    # 'mem_used': re.compile('MEMused\(GB\): (\d+)\s?;?'),
}

dt_pattern = re.compile('\[.+?\]')

with open(session_log, 'r') as slf:
    with open(sessions_csv, 'w') as scf:
        csv_headers = ','.join(sorted(patterns))
        scf.write(f'date,time,{csv_headers}\n')
        for line in slf:
            dt = dt_pattern.findall(line)[0]
            if line.find('EST') > -1:
                dt = datetime.strptime(dt, '[%a %b %d %H:%M:%S EST %Y]')
            elif line.find('EDT') > -1:
                dt = datetime.strptime(dt, '[%a %b %d %H:%M:%S EDT %Y]')
            date = dt.strftime('%Y-%m-%d')
            time = dt.strftime('%H:%M:%S')
            matches = []
            for ptrn in sorted(patterns):
                try:
                    match = patterns[ptrn].findall(line)[0]
                except IndexError:
                    match = '0'
                matches.append(match)
            csv_line = ','.join(matches)
            scf.write(f'{date},{time},{csv_line}\n')


