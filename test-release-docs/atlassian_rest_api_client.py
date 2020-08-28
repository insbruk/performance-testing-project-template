import os
from atlassian.rest_client import AtlassianRestAPI


jira2 = AtlassianRestAPI(
    url='https://jira.example.com',
    username=os.getlogin(),
    password=''
)
