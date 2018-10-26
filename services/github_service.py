from services.text_enrichment_service import enrich_comment
import config
import datetime
import urllib.request
import urllib.parse
import json

def exchange_code_to_token(code):
    if code == None or code == '':
        return None
    
    try:
        print(config.get_github_client_secret())
        data = {'client_id': config.get_github_client_id(), 'client_secret': config.get_github_client_secret(), 'code': code}
        req = urllib.request.Request('https://github.com/login/oauth/access_token', urllib.parse.urlencode(data).encode('utf-8'))
        req.add_header('Accept', 'application/json')
        response = urllib.request.urlopen(req).read()
        content = json.loads(response)
        return content['access_token']
    except Exception as e:
        print(e)
        return None

def get_not_merged_prs_count(access_token=None):
    url = __add_token('https://api.github.com/search/issues?q=repo:cms-sw/cmssw+is:pr+state:open+label:dqm-approved', access_token)
    response = urllib.request.urlopen(url).read()
    content = json.loads(response)
    return content['total_count']

def get_prs(access_token=None):
    url = __add_token('https://api.github.com/search/issues?q=repo:cms-sw/cmssw+is:pr+state:open+label:dqm-pending', access_token)
    response = urllib.request.urlopen(url).read()
    content = json.loads(response)
    pending = content['items']
    
    url = __add_token('https://api.github.com/search/issues?q=repo:cms-sw/cmssw+is:pr+state:open+label:dqm-rejected', access_token)
    response = urllib.request.urlopen(url).read()
    content = json.loads(response)
    rejected = content['items']

    prs = pending + rejected
    for pr in prs:
        pr['body'] = enrich_comment(pr['body'])
    
    return prs

def get_last_comment(url, updated_at, access_token=None):
    since = datetime.datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
    since -= datetime.timedelta(minutes=30)
    since = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    url = __add_token(url + '?since=' + since, access_token)
    response = urllib.request.urlopen(url).read()

    content = json.loads(response)
    
    if len(content) > 0:
        return content[-1]
    else:
        return None

def get_issues(access_token=None):
    url = __add_token('https://api.github.com/search/issues?q=repo:cms-sw/cmssw+is:issue+state:open+label:dqm-pending', access_token)
    response = urllib.request.urlopen(url).read()
    content = json.loads(response)
    issues = content['items']

    for issue in issues:
        issue['body'] = enrich_comment(issue['body'])
    
    return issues

def __add_token(url, access_token):
    if access_token != None and access_token != '':
        return url + '&access_token=' + access_token
    else:
        return url
