import os; import sys; sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))
import json
import time
from lib.microfocus import PerfCenter
from pprint import pprint


alm_domain, alm_project, alm_test = sys.argv[1:]
prfctr = PerfCenter(
    url='http://host01.example.com',
    domain="DOMAIN1",
    project="PROJECT1"
)
prfctr.authenticate(
    login='perftest',
    password='perftest'
)
# r = prfctr.get_test_run_status_extended(run_id=1304)
# print(r.json())
# exit()
with open('../../environment/performance.json', 'r') as f:
    tests = json.load(f)
r = prfctr.start_test_run(
    duration_hours=tests[alm_test]['duration'].split('')[0],
    duration_mins=tests[alm_test]['duration'].split('')[1],
    test_instance_id=tests[alm_test]['test-instance-id'],
    test_id=tests[alm_test]['test-id'],
    post_run_action=tests[alm_test]['post-run-action'])
pprint(r)
test_run_id = r.json()['ID']
test_timeslot_id = r.json()['TimeslotID']

r = prfctr.get_test_run_status_extended(run_id=test_run_id).json()
test_run_state = r['RunState']

while test_run_state == 'Initializing' or test_run_state == 'Running':
    r = prfctr.get_test_run_status_extended(run_id=test_run_id).json()
    pprint(r)
    total_passed_transactions = r['TotalPassedTransactions']
    total_failed_transactions = r['TotalFailedTransactions']
    try:
        if total_failed_transactions/(total_passed_transactions+total_failed_transactions)*100 > 3:
            prfctr.stop_test_run(run_id=test_run_id)
            test_run_state = 'Stopping'
    except ZeroDivisionError:
        pass
    # {'ID': 1303, 'Duration': 0, 'RunState': 'Initializing', 'RunSLAStatus': '', 'StartTime': '2019-09-26 10:49:21',
    #  'EndTime': '2019-09-26 10:49:22', 'MaxVusers': 0.0, 'TotalPassedTransactions': 0.0, 'TotalFailedTransactions': 0.0,
    #  'TotalErrors': 0.0, 'AverageHitsPerSecond': 0.0, 'AverageThroughputPerSecond': 0.0, 'TestID': 121,
    #  'TestInstanceID': 53, 'PostRunAction': 'Collate And Analyze', 'TimeslotID': 2451, 'VudsMode': False}
    time.sleep(300)

while test_run_state != 'Stopping' or test_run_state != 'Before Collating Results' or test_run_state != 'Before Creating Analysis Data':
    r = prfctr.get_test_run_status_extended(run_id=test_run_id).json()
    pprint(r)
    test_run_state = r['RunState']
    pprint(r)
    time.sleep(60)

if test_run_state == 'Before Collating Results':
    r = prfctr.collate_test_results(run_id=test_run_id).json()
    pprint(r)
    time.sleep(60)

pprint(r)