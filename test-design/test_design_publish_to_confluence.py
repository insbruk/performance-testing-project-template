import atlassian

collection = [
    {
        'service': 'auth-service',
        'class': 'AuthController',
        'method': 'login',
        'endpoint': 'POST /api/v1/auth/login',
        'tph': 5000,
        'sla': 2000
    },
    {
        'service': 'meta-service',
        'class': 'MetaController',
        'method': 'getMetaData',
        'endpoint': 'GET /api/v1/meta/{uuid}',
        'tph': 1000,
        'sla': 2000
    },
    {
        'service': 'search-service',
        'class': 'SearchController',
        'method': 'searchItems',
        'endpoint': 'POST /api/v1/search',
        'tph': 2000,
        'sla': 2000
    },
    {
        'service': 'content-service',
        'class': 'ContentController',
        'method': 'getResource',
        'endpoint': 'GET /api/v1/content/{uuid}',
        'tph': 10000,
        'sla': 2000
    },
]

cnfl_parent_page_id = 100000
cnfl_page_title = f'Performance Test Design'

confluence = atlassian.confluence.Confluence(
    url='https://confluence.example.com',
    username='perftest',
    password='perftest'
)

table_rows = ''
for api in collection:
    table_rows += f'''
<tr>
    <th>{api["service"]}</th> 
    <td>{api["class"]}.{api["method"]}()</td> 
    <td>{api["endpoint"]}</td> 
    <td>{api["tph"]}</td> 
    <td>{api["sla"]}</td> 
</tr>
'''

cnfl_page_xml = f'''
<ac:layout>
    <ac:layout-section ac:type="single">
        <ac:layout-cell>
            <table>
                <tbody>
                    <tr>   
                        <th colspan="2"><h3 style="text-align: center;">Performance test workload for </h3></th> 
                    </tr>
                    <tr> 
                        <th>Description</th> 
                        <td></td>
                    </tr>
                    <tr> 
                        <th>Based on Prod Stat</th> 
                        <td></td>
                    </tr>
                    <tr> 
                        <th>Workload Model</th> 
                        <td><ac:image ac:width="780"><ri:attachment ri:filename="test_design.png"/></ac:image></td>
                    </tr>
                    <tr> 
                        <th>Ramp up</th> 
                        <td>5 min</td>
                    </tr>
                    <tr> 
                        <th>Steady state</th> 
                        <td>6 hours</td>
                    </tr>
                    <tr> 
                        <th>Ramp down</th> 
                        <td>5 min</td>
                    </tr>
                </tbody>
            </table>
            <table>
                <tbody>
                    <tr> 
                        <th>Service</th> 
                        <th>Class/Method</th> 
                        <th>Endpoint</th> 
                        <th>TPH</th> 
                        <th>SLA</th> 
                    </tr>
                    {table_rows}
                </tbody>
            </table>
        </ac:layout-cell>
    </ac:layout-section>
</ac:layout>
'''

confluence.update_or_create(
    parent_id=cnfl_parent_page_id,
    title=cnfl_page_title,
    body=cnfl_page_xml,
)

cnfl_page_test_design = confluence.get_page_by_title(
    space='PTAT',
    title=cnfl_page_title
)
cnfl_page_id = cnfl_page_test_design['id']
confluence.attach_file(
    filename='test_design.png',
    page_id=cnfl_page_id,
)
