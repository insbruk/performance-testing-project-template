import re
import sys
import json
import plotly
import base64
import requests
import atlassian
from pprint import pprint
from datetime import datetime
from dateutil.tz import tzutc, gettz


def base64_encode_credentials(username='', password=''):
    return base64.b64encode(f"{username}:{password}".encode("unicode_escape")).decode("utf-8")


elastic = {
    'prod': {
        'url': 'https://jupiterq.aws.example.com:9200',
        'username': 'perftest',
        'password': 'perftest',
    },
    'perf': {
        'url': 'https://jupiterq.aws.example.com:9200',
        'username': 'perftest',
        'password': 'perftest',
    }
}
dt_timezone = 'America/New_York'
dt_format = '%Y/%m/%dT%H:%M:%S'
environment, service, period, day_of_period = sys.argv[1:]
# period = '2019/09/02T05:00:00-2019/09/09T05:00:00'
# day_of_period = '2019/09/04T05:00:00-2019/09/05T05:00:00'
# day_of_period = 'None'
period_start = period.split('-')[0]
period_end = period.split('-')[1]

if day_of_period == 'None':
    interval = '1h'
    graph_name = 'requests per hour'
    period_dto_start = datetime.strptime(period_start, dt_format).replace(tzinfo=gettz(dt_timezone))
    period_dto_end = datetime.strptime(period_end, dt_format).replace(tzinfo=gettz(dt_timezone))
    tstamp_start, tstamp_end = int(period_dto_start.timestamp() * 1000), int(period_dto_end.timestamp() * 1000)
    cnfl_dt_start, cnfl_dt_end = period_start.split('T')[0], period_end.split('T')[0]
    cnfl_parent_title = f'app prod stat {cnfl_dt_start} - {cnfl_dt_end}'
    cnfl_prod_stat_title = f'{service} {cnfl_dt_start} - {cnfl_dt_end}'
elif day_of_period != 'None':
    interval = '1m'
    graph_name = 'requests per min'
    day_of_period_dto_start = datetime.strptime(day_of_period.split('-')[0], dt_format).replace(tzinfo=gettz(dt_timezone))
    day_of_period_dto_end = datetime.strptime(day_of_period.split('-')[1], dt_format).replace(tzinfo=gettz(dt_timezone))
    tstamp_start, tstamp_end = int(day_of_period_dto_start.timestamp() * 1000), int(day_of_period_dto_end.timestamp() * 1000)
    cnfl_parent_title = f'{service} {period_start.split("T")[0]} - {period_end.split("T")[0]}'
    cnfl_prod_stat_title = f'{service} prod stat {day_of_period.split("-")[0].split("T")[0]}'

confluence = atlassian.confluence.Confluence(
    url='https://confluence.example.com',
    username='perftest',
    password='perftest'
)

elastic_url = elastic[environment]['url']
elastic_credentials = base64_encode_credentials(
    username=elastic[environment]['username'],
    password=elastic[environment]['password']
)
elastic_auth_header = {
    'Authorization': f'Basic {elastic_credentials}'
}
elastic_session = requests.session()
elastic_session.headers.update(elastic_auth_header)
elastic_session.verify = False

with open('api.json', 'r') as f:
    api = json.load(f)

params = {
    'aggs': {
        '2': {
            'date_histogram': {
                'field': '@timestamp',
                'time_zone': dt_timezone,
                'interval': interval,
            }
        }
    },
    'query': {
        'bool': {
            'must': [
                {
                    'query_string': {
                        'query': 'filter',
                        'analyze_wildcard': 'true',
                        'default_field': '*'
                    }
                },
                {
                    'match_phrase': {
                        'application': {
                            'query': 'access'
                        }
                    }
                },
                {
                    'match_phrase': {
                        'applicationEnvironment': {
                            'query': 'prod'
                        }
                    }
                },
                {
                    'range': {
                        '@timestamp': {
                            'gte': tstamp_start,
                            'lte': tstamp_end,
                            'format': 'epoch_millis'
                        }
                    }
                }
            ],
            'filter': [],
            'should': [],
            'must_not': []
        }
    },
}

charts = ''
for req in api[service]:
    params['query']['bool']['must'][0]['query_string']['query'] = req['filter']
    response = elastic_session.post(
        url=f'{elastic_url}/app-*/_search?size=0',
        json=params,
    )
    print(response.url, req['filter'], response.status_code)
    request_total = response.json()['hits']['total']
    request_stat = response.json()['aggregations']['2']['buckets']
    x = [v['key_as_string'] for v in request_stat]
    y = [v['doc_count'] for v in request_stat]
    data = []
    graph_trace = plotly.graph_objs.Bar(
        x=x,
        y=y,
        name=graph_name,
    )
    data.append(graph_trace)
    chart = plotly.offline.plot(
        {
            "data": data,
            "layout": plotly.graph_objs.Layout(
                title=f'{req["class.method"]}: {graph_name}'
            )
        },
        include_plotlyjs=False,
        output_type='div',
        show_link=False,
    )
    caption = f'''
    <p>
        <h3>Requests: {req["request"]}</h3>
        <h4>ELK Filter: {req["filter"]}</h4>
    </p>
    '''
    charts += chart + caption

print(cnfl_parent_title)
cnfl_parent_page = confluence.get_page_by_title(
    space='PTAT',
    title=cnfl_parent_title
)
cnfl_parent_page_id = cnfl_parent_page['id']

# cnfl_stat_page = confluence.get_page_by_title(
#     space='PTAT',
#     title=f'app prod stat 2019/08/26 - 2019/09/02'
# )
# cnfl_stat_page_id = cnfl_stat_page['id']
# title = f'{service} {date_cnfl}'

cnfl_page = f'''
    <ac:structured-macro ac:name='html'>
        <ac:plain-text-body>
            <![CDATA[<script src="https://cdn.plot.ly/plotly-1.49.2.min.js"></script>]]>
        </ac:plain-text-body>
    </ac:structured-macro>
    <ac:structured-macro ac:name='html'>
        <ac:plain-text-body>
            <![CDATA[{charts}]]>
        </ac:plain-text-body>
    </ac:structured-macro>
'''

confluence.update_or_create(
    parent_id=cnfl_parent_page_id,
    title=cnfl_prod_stat_title,
    body=cnfl_page,
)
