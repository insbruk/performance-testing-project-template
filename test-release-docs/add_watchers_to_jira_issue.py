import os
from pprint import pprint
from atlassian import Jira


jira = Jira(
    url='https://jira.example.com',
    username=os.getlogin(),
    password=input('Please enter password: ').strip()
)

watchers = [
    'user1',
    'user2',
    'user3',
]

for w in watchers:
    data = jira.issue_add_watcher(
        issue_key='PRJ-1000',
        user=w,
    )
    pprint(data)