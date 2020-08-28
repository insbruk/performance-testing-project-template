import os
import sys
import bs4
import json
import boto3
import shutil
import jinja2
import requests
import atlassian
import mysql.connector
from dateutil.tz import tzutc, gettz
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))
from lib.microfocus import PerfCenter
from lib.grafana import Grafana

alm_domain, alm_project, alm_test, alm_run_id, cnfl_sprint_num, = sys.argv[1:]
aws_asg_client = boto3.client('autoscaling', 'us-east-1')
aws_ec2_client = boto3.client('ec2', 'us-east-1')
with open('../../environment/performance.json', 'r') as f:
    tests = json.load(f)
with open('../../environment/environment.json', 'r') as f:
    environment = json.load(f)
dependencies = tests[alm_test]['dependencies']
test_tz = 'America/New_York'
dt_format = '%Y-%m-%d %H:%M:%S'
use_proxy = False
if use_proxy:
    proxies = {
        'https': 'https://proxy-dev.aws.example.com:8080',
        'http': 'http://proxy-dev.aws.example.com:8080',
    }
else:
    proxies = {}
mysql_db = mysql.connector.connect(
    host='host',
    user="user",
    passwd="password"
)
mysql_db_cursor = mysql_db.cursor()
mysql_db_cursor.execute('SELECT LIQUIBASE FROM app.databasechangelog order by DATEEXECUTED desc LIMIT 1;')
mysql_db_schema_version = mysql_db_cursor.fetchone()[0]
environment['app-mysql-db']['schema'] = mysql_db_schema_version
mysql_db_cursor.close()
mysql_db.close()
jinja_environment = jinja2.Environment(
    loader=jinja2.PackageLoader('report-generator', 'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)
test_report_template = jinja_environment.get_template(
    name=f'test-report-template.xml'
)
prfctr = PerfCenter(
    host='http://car-wnaslreq-04.example.com',
    domain="domain",
    project="project"
)
prfctr.authenticate(
    login='perftest',
    password='perftest'
)
confluence = atlassian.confluence.Confluence(
    url='https://confluence.example.com',
    username='perftest',
    password='perftest'
)
grafana = Grafana(
    url='http://grafana.aws.example.com:3000',
    auth_header='Token'
)

# clean workspace
try:
    shutil.rmtree('Report')
except FileNotFoundError:
    pass
try:
    os.remove('Reports.zip')
    os.remove('Report.html')
except FileNotFoundError:
    pass
old_images = [f for f in os.listdir() if f.endswith('.png')]
for img in old_images:
    os.remove(img)

r = prfctr.get_test_run_status_extended(run_id=alm_run_id).json()
datetime_start = datetime.strptime(r['StartTime'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=gettz(test_tz)) - timedelta(
    minutes=10)
datetime_start_utc = datetime_start.astimezone(timezone.utc)
datetime_end = datetime.strptime(r['EndTime'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=gettz(test_tz)) + timedelta(
    minutes=10)
datetime_end_utc = datetime_end.astimezone(timezone.utc)
duration = datetime.strptime(r['EndTime'], dt_format) - datetime.strptime(r['StartTime'], dt_format)
test = {
    'id': r['TestID'],
    'run_id': r['ID'],
    'end_time': r['EndTime'],
    'start_time': r['StartTime'],
    'ts_start_time': (round(datetime.timestamp(datetime_start))) * 1000,
    'ts_end_time': (round(datetime.timestamp(datetime_end))) * 1000,
    'duration': duration,
    'total_errors': r['TotalErrors'],
    'total_passed_transactions': r['TotalPassedTransactions'],
    'total_failed_transactions': r['TotalFailedTransactions'],
    'name': prfctr.get_test_design(test_id=r['TestID'], accept='application/json').json()['Name']
}

for app in dependencies:
    try:
        test_period = f';gtf=c_{test["ts_start_time"]}_{test["ts_end_time"]}'
        environment[app]['dashboard']['dynatrace-perf'] += f'{test_period}'
    except KeyError:
        pass
    try:
        test_period = f';start={datetime_start_utc.strftime("%Y-%m-%dT%H:%M:%SZ")};end={datetime_end_utc.strftime("%Y-%m-%dT%H:%M:%SZ")}'
        environment[app]['dashboard']['cloudwatch'] += f'{test_period}'
    except KeyError:
        pass

for app in dependencies:
    # describe versions
    try:
        app_version = environment[app]['version']
    except KeyError:
        app_version = None
    try:
        app_check_version_url = environment[app]['check_version_url']
    except KeyError:
        app_check_version_url = None
    if not app_version and app_check_version_url:
        print(app, app_check_version_url)
        try:
            app_version_json = requests.get(url=app_check_version_url, proxies=proxies).json()
            app_version = [app_version_json[attr] for attr in app_version_json if attr.lower().find('version') > -1][0]
        except json.decoder.JSONDecodeError:
            app_version = None
    try:
        environment[app]['version'] = app_version
    except KeyError:
        pass

for app in dependencies:
    # describe instances
    try:
        asg = environment[app]['[AWS]AutoScalingGroup']
        r = aws_asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg, ])
        if r['AutoScalingGroups']:
            environment[app]['instances'] = [instance['InstanceId'] for instance in
                                             r['AutoScalingGroups'][0]['Instances']]
    except KeyError:
        pass

for app in dependencies:
    # create graphs
    try:
        if len(environment[app]['instances']) > 0:
            grafana.get_instances_graphs(
                app=app,
                instance_list=environment[app]['instances'],
                tz=test_tz,
                ts_start=test['ts_start_time'],
                ts_end=test['ts_end_time'],
            )
    except KeyError:
        pass
    if 'mysql' in app:
        grafana.get_mysql_graphs(
            db_name=app,
            db_id=environment[app]['id'],
            tz=test_tz,
            ts_start=test['ts_start_time'],
            ts_end=test['ts_end_time'],
        )

# upload graphs
images_to_upload = []
files = [f for f in os.listdir() if f.endswith('.png')]
files.sort()
for dep in dependencies:
    for f in files:
        if f.startswith(dep):
            images_to_upload.append(f)
resource_utilization = [
    {
        'file': f,
        'name': f.split('.')[0].replace('-', ' ')
    }
    for f in images_to_upload
]
print(resource_utilization)

lr_test_results = []
http_responses_summary = 'job was not able to download html report or extract data'
transaction_summary = 'job was not able to download html report or extract data'

try:
    r = prfctr.download_test_results_files(run_id=alm_run_id, files=['Reports.zip'], dst='')
    with open('Report/summary.html', 'r') as f:
        summary_html = f.read()
        summary_soup = bs4.BeautifulSoup(summary_html, 'lxml')
        transaction_summary = summary_soup.find('table', {'summary': 'Transactions statistics summary table'})
        for i in transaction_summary.find_all('tr'):
            i.attrs = {}
            i.find_all('td')[0].name = 'th'
            i.find_all('td')[0].extract()
            i.find_all('td')[3].extract()
            i.find_all('td')[6].extract()
        for i in transaction_summary.tr.find_all('td'):
            i.name = 'th'
        transaction_summary.attrs = {}
        http_responses_summary = summary_soup.find('table', {'summary': 'HTTP responses summary table'})
        try:
            http_responses_summary.attrs = {}
            http_responses_summary.tr.attrs = {}
            for i in http_responses_summary.find_all('tr'):
                i.attrs = {}
                i.find_all('td')[0].name = 'th'
            for i in http_responses_summary.tr.find_all('td'):
                i.name = 'th'
        except AttributeError:
            http_responses_summary = 'There is no http responses summary table in html report'

    with open('Report/contents.html') as f:
        contents_html = f.read()
    contents_soup = bs4.BeautifulSoup(contents_html, 'lxml')
    contents_summary = contents_soup.find('div', {'id': 'mySidenav'})
    contents_summary.find('a', href=True).decompose()
    for content in contents_summary.find_all('a', href=True):
        graph_report = content['href']
        graph_name = content.div.text
        print(graph_report, graph_name)
        # with open(f'Report/{graph_report}') as f:
        #     graph_html = f.read()
        # graph_soup = bs4.BeautifulSoup(graph_html, 'lxml')
        # graph_legend = graph_soup.find('table', {'class': 'legendTable'})
        # try:
        #     graph_legend.name = 'tbody'
        # except AttributeError:
        #     continue
        # graph_legend_rows = graph_legend.find_all('tr')
        # for r in graph_legend_rows:
        #     td = r.find('td')
        #     td.extract()
        # graph_legend_row = graph_legend.find('tr')
        # graph_legend_headers = graph_legend_row.find_all('td')
        # for td in graph_legend_headers:
        #     td.name = 'th'
        # graph_legend = graph_legend.prettify()
        # graph_legend = f'<table>{graph_legend}</table>'
        lr_test_results.append(
            {
                'name': graph_name,
                'filename': f'{graph_name.lower().replace(" ", "_")}.jpg',
                'legend': ''
            }
        )
except IndexError:
    pass

cnfl_report_body = test_report_template.render(
    test=test,
    apps=dependencies,
    environment=environment,
    lr_test_results=lr_test_results,
    resource_utilization=resource_utilization,
    http_responses_summary=http_responses_summary,
    transaction_summary=transaction_summary,
)
cnfl_sprint_title = f'Release {cnfl_sprint_num}'
cnfl_sprint_page = confluence.get_page_by_title(
    space='PT',
    title=cnfl_sprint_title
)
cnfl_sprint_page_id = cnfl_sprint_page['id']
cnfl_report_title = f'{alm_run_id} {test["name"]}'
confluence.update_or_create(
    parent_id=cnfl_sprint_page_id,
    title=cnfl_report_title,
    body=cnfl_report_body,
)
cnfl_report_page = confluence.get_page_by_title(
    space='PTAT',
    title=cnfl_report_title
)
cnfl_report_page_id = cnfl_report_page['id']
for img in images_to_upload:
    print(f'Uploading {img} ...')
    confluence.attach_file(
        filename=img,
        page_id=cnfl_report_page_id,
    )
for img in images_to_upload:
    try:
        os.remove(img)
    except FileNotFoundError:
        continue

prfctr.logout()
