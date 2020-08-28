import bs4

lr_test_results = []

with open('Report/contents.html') as f:
    contents_html = f.read()
contents_soup = bs4.BeautifulSoup(contents_html, 'lxml')
contents_summary = contents_soup.find('div', {'id': 'mySidenav'})
contents_summary.find('a', href=True).decompose()
for content in contents_summary.find_all('a', href=True):
    graph_report = content['href']
    graph_name = content.div.text
    print(graph_report, graph_name)
    with open(f'Report/{graph_report}') as f:
        graph_html = f.read()
    graph_soup = bs4.BeautifulSoup(graph_html, 'lxml')
    graph_legend = graph_soup.find('table', {'class': 'legendTable'})
    graph_legend.name = 'tbody'

    graph_legend_rows = graph_legend.find_all('tr')
    for r in graph_legend_rows:
        td = r.find('td')
        td.extract()
    graph_legend_row = graph_legend.find('tr')
    graph_legend_headers = graph_legend_row.find_all('td')
    for td in graph_legend_headers:
        td.name = 'th'
    graph_legend = graph_legend.prettify()
    print(f'<table>{graph_legend}</table>')
    exit()
    lr_test_results.append(
        {
            'name': graph_name,
            'filename': f'{graph_name.lower().replace(" ", "_")}.jpg',
            'legend': graph_legend
        }
    )

# print(graph_legend.prettify())