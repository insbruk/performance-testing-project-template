import plotly
import plotly.graph_objs as go
import pandas


session_csv_file = 'uni_session.csv'

periods = [
    '2020-01',
    '2020-02',
    '2020-03',
]

users = [
    'admin',
    'assistant',
    'instructor',
    'student',
]

with open(session_csv_file, 'r') as f:
    line = f.readline().split(',')
    csv_headers = [header.strip() for header in line]
    csv_headers = enumerate(csv_headers)
    csv_headers = {header[1]: header[0] for header in csv_headers}
for period in periods:
    for user in users:
        print(f'Period - {period}, User - {user}')
        df = pandas.read_csv(session_csv_file, sep=',')
        user_period = [f'{row[0]} {row[1]}' for row in df.values if row[0].find(period) > -1]
        user_values = [row[csv_headers[user]] for row in df.values if row[0].find(period) > -1]

        user_data = go.Bar(
            x=user_period,
            y=user_values,
            name=f'{user.capitalize()} Sessions.',
            marker=dict(
                color='rgb(50,200,125)'
            )
        )

        data = [user_data]
        layout = go.Layout(
            title=f'{period} {user.capitalize()} Sessions.',
            xaxis=dict(tickangle=-45),
            barmode='group',
        )
        figure = go.Figure(data=data, layout=layout)

        plotly.offline.plot(figure, filename=f'{period}_{user}_sessions.html')