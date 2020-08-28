import sys
import atlassian

capture_versions = True
jenkins = False
if jenkins:
    release = sys.argv[1:][0]
else:
    release = "1.105"
username = 'perftest'
password = 'perftest'
# username = os.getlogin()
# password=input('Please enter password: ').strip()
jira = atlassian.jira.Jira(
    url='https://jira.example.com',
    username=username,
    password=password
)
sprint_label = f'RELEASE-{release}'

components = {
    'CORE': '18824',
    'Admin': '18724',
    'LTI': '18837',
}

sprint = {
    'labels': [
        sprint_label,
    ],
    'watchers': [
        'user1',
        'user2',
        'user3',
    ],
    'tasks': [
        {
            'task_name': f'[App1 {release} RC] Performance Testing',
            'test_name': 'Performance Test 10000u',
            'test_workload': 'https://confluence.example.com/x/JR5VAw',
            'components': [
                {'id': components['LTI']},
            ],
        },
        {
            'task_name': f'[App2 {release} RC] Performance Testing',
            'test_name': 'Performance Test 3600u',
            'test_workload': 'https://confluence.example.com/x/dBStB',
            'components': [
                {'id': components['Admin']},
                {'id': components['LTI']},
                {'id': components['CORE']},
            ],
        },
    ]
}

for task in sprint['tasks']:
    fields = {
        'summary': task['task_name'].format(release),
        'assignee': {
            'name': 'unassigned'
        },
        'project': {
            'id': '10600'
        },
        'issuetype': {
            'id': '3'
        },
        'components': task['components'],
        'labels': sprint['labels'],
        'description': f"*Performance Test:* [{task['test_name']}|{task['test_workload']}]",
    }
    data = jira.issue_create(
        fields=fields,
    )
    print(data)
    issue_key = data['key']
    for w in sprint['watchers']:
        data = jira.issue_add_watcher(
            issue_key=issue_key,
            user=w,
        )
        print(data)
