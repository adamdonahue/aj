from jira.client import JIRA
import getpass

options = {
        'server': 'https://jira.corp.appnexus.com',
        }

jira = JIRA(options, basic_auth=('adonahue',getpass.getpass()))

issue = {
        'project': {'key': 'DO'},
        'summary': 'hi kayla)',
        'description': 'A test issue for adding comments',
        'issuetype': {'name': 'Bug'}
        }

issue = jira.create_issue(fields=issue)
#issue = jira.issue('DO-28')

print dir(issue)
