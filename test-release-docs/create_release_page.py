import sys
import atlassian

capture_versions = True
jenkins = False
if jenkins:
    release = sys.argv[1:][0]
else:
    release = "5.105"

release_name = f'App Release {release}'
app1_release_name = f'APP1 Release {release}'
app2_release_name = f'APP2 Release {release}'
app3_release_name = f'APP3 Release {release}'
release_perf_label = f'APP-RELEASE-{release}'
sprint = release.split(".")[1]
sprint_name = f'Sprint {sprint}'
sprint_hob = f'HOB {sprint}'

username = 'perftest'
password = 'perftest'
confluence = atlassian.confluence.Confluence(
    url='https://confluence.example.com',
    username=username,
    password=password,
    # username = os.getlogin(),
    # password=input('Please enter password: ').strip()
)

body = f'''
<ac:layout>
    <ac:layout-section ac:type="two_right_sidebar">
        <ac:layout-cell>
            <table>
                <tbody>
                    <tr>
                        <th colspan="2"><h2>Release Details</h2></th>
                    </tr>
                    <tr>
                        <th>Deployment</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Release Manager</th>
                        <td><ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link></td>
                    </tr>
                    <tr>
                        <th>Release Document</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th>Release Management</th>
                        <td><a href="https://confluence.example.com/x/35P-BQ">All Releases</a></td>
                    </tr>
                    <tr>
                        <th>Scrum Teams</th>
                        <td><a href="https://confluence.example.com/x/GgUUBQ">Teams Structure</a></td>
                    </tr>
                    <tr>
                        <th>Product Owners</th>
                        <td>
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>,
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>,
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>,
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>,
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>
                        </td>
                    </tr>
                    <tr>
                        <th>Performance Lead, Manager</th>
                        <td>
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>,
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>
                        </td>
                    </tr>
                    <tr>
                        <th>Performance Engineers</th>
                        <td>
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>,
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>,
                            <ac:link><ri:user ri:userkey="{confluence.get_user_details_by_username('user1')['userKey']}"/></ac:link>
                        </td>
                    </tr>
                </tbody>
            </table>
        </ac:layout-cell>
        <ac:layout-cell>
            <ac:structured-macro ac:name="toc">
                <ac:parameter ac:name="type">list</ac:parameter>
                <ac:parameter ac:name="style">square</ac:parameter>
                <ac:parameter ac:name="minLevel">1</ac:parameter>
                <ac:parameter ac:name="maxLevel">4</ac:parameter>
                <ac:parameter ac:name="printable">true</ac:parameter>
                <ac:parameter ac:name="indent">25px</ac:parameter>
                <ac:parameter ac:name="class">bigpink</ac:parameter>
                <ac:parameter ac:name="outline">false</ac:parameter>
            </ac:structured-macro>
        </ac:layout-cell>
    </ac:layout-section>
    <ac:layout-section ac:type="single">
        <ac:layout-cell>
            <h2>Performance Testing Status</h2>        
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,assignee,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project = PT and labels={release_perf_label}</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>

            <h2>{app2_release_name} Bugs</h2>            
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=NG and Sprint in ('{sprint_name}', '{sprint_hob}') and type in (Bug) order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>

            <h2>{app2_release_name} Tasks, Change Requests</h2>
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=NG and Sprint in ('{sprint_name}', '{sprint_hob}') and type in (Task, Spike, 'Change Request') order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>

            <h2>{app2_release_name} Epics, Stories, Features, Improvements</h2>
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=NG and Sprint in ('{sprint_name}', '{sprint_hob}') and type in (Epic, Story, Feature, Improvement) order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>

            <h2>{app1_release_name} Bugs</h2>
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=LMS and Sprint in ('{sprint_name}') and type in (Bug) order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>
            
            <h2>{app1_release_name} Tasks, Change Requests</h2>
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=LMS and Sprint in ('{sprint_name}') and type in (Task, Spike, 'Change Request') order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>
            
            <h2>{app1_release_name} Epics, Stories, Features, Improvements</h2>
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=LMS and Sprint in ('{sprint_name}') and type in (Epic, Story, Feature, Improvement) order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>

            <h2>{app3_release_name} Bugs</h2>
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=EQAT and Sprint in ('{sprint_name}') and type in (Bug) order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>
            
            <h2>{app3_release_name} Tasks, Change Requests</h2>
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=EQAT and Sprint in ('{sprint_name}') and type in (Task, Spike, 'Change Request') order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>
            
            <h2>{app3_release_name} Epics, Stories, Features, Improvements</h2>
            <ac:structured-macro ac:name="jira">
                <ac:parameter ac:name="columns">key,summary,type,scrum team,priority,status</ac:parameter>
                <ac:parameter ac:name="jqlQuery">project=EQAT and Sprint in ('{sprint_name}') and type in (Epic, Story, Feature, Improvement) order by 'Scrum Team', priority DESC</ac:parameter>
                <ac:parameter ac:name="maximumIssues">50</ac:parameter>
            </ac:structured-macro>
        </ac:layout-cell>
    </ac:layout-section>
</ac:layout>
'''

status = confluence.update_or_create(
    title=release_name,
    body=body,
    parent_id=71023619
)
print(status)
