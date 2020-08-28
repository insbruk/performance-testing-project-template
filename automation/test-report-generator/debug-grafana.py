import os; import sys; sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))
import json
from lib.grafana import Grafana


grafana = Grafana(
    url='http://grafana.aws.example.com:3000',
    auth_header='Token'
)
alm_test = 'was'
tests_json = '../../environment/performance.json'
environment_json = '../../environment/environment.json'
with open(tests_json, 'r') as f:
    tests = json.load(f)
with open(environment_json, 'r') as f:
    environment = json.load(f)

dependencies = tests[alm_test]['dependencies']

for app in dependencies:
    if 'mysql' in app:
        grafana.get_mysql_graphs(
                    db_name=app,
                    db_id=environment[app]['id'],
                    tz='America/New_York',
                    ts_start=1575022828137,
                    ts_end=1575044428137,
                )