# https://developer.atlassian.com/server/jira/platform/rest-apis/
import os
import json
from pprint import pprint
from atlassian import Jira


jira = Jira(
    url='https://jira.example.com',
    username=os.getlogin(),
    password=input('Please enter password: ').strip()
)

fields = {
        'summary': 'Test Summary',
        'assignee': {
            'name': 'unassigned'
        },
        'project': {
            'id': '10600'
        },
        'issuetype': {
            'id': '3'
        },
        'components': [
            {'id': '000'},
        ],
        'labels': [
            'test-label',
        ],
        'description': 'Test Description',
    }

data = jira.issue_update(
    issue_key='PT-0000',
    fields=fields,
)