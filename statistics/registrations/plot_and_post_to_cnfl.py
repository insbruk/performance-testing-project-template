import os
import csv
import plotly
from atlassian import Confluence


reg_max_per_day = 'reg_max_per_day.csv'
regs_per_day = 'regs_per_day.csv'
registrations = 'registrations.csv'
cnfl_parent_id = 69377983
cnfl_page_id = 92093567
confluence = Confluence(
    url='https://confluence.example.com',
    username=os.getlogin(),
    password=input('Please enter password for Confluence: ').strip(),
    # password='',
)
# plot graph metric per Day
dates, regs = [], []
with open(regs_per_day, 'r', newline='') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        date, regs_count = row['date'], row['regs']
        dates.append(date)
        regs.append(regs_count)
data = []
graph_trace = plotly.graph_objs.Bar(
    x=dates,
    y=regs,
    name=f'User Registrations per Day',
)
data.append(graph_trace)
html_chart = plotly.offline.plot(
    {
        "data": data,
        "layout": plotly.graph_objs.Layout(title=f'User Registrations per Day. Total {sum([int(r) for r in regs])}.')
    },
    include_plotlyjs=False,
    output_type='div',
    show_link=False,
)
# plot graphs 'User Registrations' for most loaded days.'
most_loaded_dates = {}
with open(reg_max_per_day, 'r', newline='') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        date, regs_count = row['date'], row['regs']
        most_loaded_dates[date] = regs_count
html_day_charts = ''
for dt in most_loaded_dates:
    dates = []
    with open(registrations, 'r', newline='') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            date = row['date']
            if date.find(dt) > -1:
                dates.append(date)
    data = []
    graph_trace = plotly.graph_objs.Histogram(
        x=dates,
        name=f'Registrations',
    )
    data.append(graph_trace)
    html_chart_day = plotly.offline.plot(
        {
            "data": data,
            "layout": plotly.graph_objs.Layout(title=f'Internal User Registrations per Hour, {dt}. Total {len(dates)}.')
        },
        include_plotlyjs=False,
        output_type='div',
        show_link=False,
    )
    html_day_charts += html_chart_day
    data = []
    graph_trace = plotly.graph_objs.Histogram(
        x=dates,
        xbins={
            'size': 60000
        },
        name=f'Registrations per Day',
    )
    data.append(graph_trace)
    html_chart_day = plotly.offline.plot(
        {
            "data": data,
            "layout": plotly.graph_objs.Layout(title=f'User Registrations per Min, {dt}. Total {len(dates)}.')
        },
        include_plotlyjs=False,
        output_type='div',
        show_link=False,
    )
    html_day_charts += html_chart_day

cnfl_page = f'''
    <ac:structured-macro ac:name='html'>
        <ac:plain-text-body>
            <![CDATA[<script src="https://cdn.plot.ly/plotly-1.49.2.min.js"></script>]]>
        </ac:plain-text-body>
    </ac:structured-macro>
    <ac:structured-macro ac:name='html'>
        <ac:plain-text-body>
            <![CDATA[{html_chart}]]>
            <![CDATA[{html_day_charts}]]>
        </ac:plain-text-body>
    </ac:structured-macro>
'''
status = confluence.update_page(
    title='Prod Stat 2019 Fall - User Registrations',
    body=cnfl_page,
    page_id=cnfl_page_id,
    parent_id=cnfl_parent_id
)
