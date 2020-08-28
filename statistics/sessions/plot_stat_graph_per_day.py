import plotly
import plotly.graph_objs as go

logfile = 'uni_session.log'

user_types = {
    'admin': 2,
    'assistant': 3,
    'instructor': 4,
    'student': 5,
}

with open(logfile, 'r') as f:
    for line in f:
        row = line.split(';')



data = []
# for ut in user_types:
timestamps = []
values = []
user_data = go.Bar(
    x=timestamps,
    y=values,
    name=f'all_users_sessions',
)
data.append(user_data)

layout = go.Layout(
    title=f'all_users_sessions',
    xaxis=dict(tickangle=-45),
    barmode='group',
)
figure = go.Figure(data=data, layout=layout)

plotly.offline.plot(figure, filename=f'all_users_sessions.html')