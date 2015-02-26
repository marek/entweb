import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask.ext.cache import Cache
from urllib import urlencode
import requests
import re
import json

class DefaultConfig(object):
    DEBUG=False
    TESTING=False
    SECRET_KEY='changeme'


app = Flask(__name__)
app.config.from_object('entweb.DefaultConfig')
app.config.from_envvar('ENTWEB_SETTINGS')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

oauth_url               = app.config['GITHUB_OAUTH_URL']
api_url                 = app.config['GITHUB_API_URL']
github_url_auth         = oauth_url+'/login/oauth/authorize'
github_url_access_token = oauth_url+'/login/oauth/access_token'
github_url_user_repos   = api_url+'/user/repos'
github_url_user_orgs    = api_url+'/user/orgs'
github_url_org_repos    = api_url+'/orgs/:org/repos'
github_url_all_repos    = api_url+'/repositories'

github_clientid = app.config['APP_CLIENTID']
github_secretid = app.config['APP_SECRETID']


def pretty_print(obj):
    print json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


def get_all(url, headers=None, params=None, max=100):
    collection = []

    while url is not None and max > 0:
        resp = requests.get(url, headers=headers, params=params, verify=False);
        collection.extend(resp.json())
        url = get_next_url(resp.headers)
        max = max - 1

    return collection


def get_next_url(headers):
    if "Link" in headers:
        header = headers["Link"]
        matches = re.match("\<(.+?)\>; rel=\"(?:next|last)\"", header)
        if matches != None:
            return matches.group(1)
    return None

@cache.memoize(300)
def get_orgs(headers):
    orgs = get_all(github_url_user_orgs, headers=headers)
    orgs.sort(key=lambda x:x['login'])
    return orgs

@cache.memoize(300)
def get_public_repos(headers):
    # Get all Public repos
    all_repos = get_all(github_url_all_repos, headers=headers, max=100)
    all_repos.sort(key=lambda x:x['full_name'])
    for repo in all_repos:
        ssh_url = repo['html_url'].replace("https://", "git@", 1)
        ssh_url = ssh_url.replace("/", ":", 1)
        ssh_url += ".git"
        repo['ssh_url'] = ssh_url
    return all_repos

@app.route('/')
def index():
    if 'github_accesstoken' not in session:
        return redirect(url_for('.login'))
    accesstoken = session['github_accesstoken']

    # Generic headers
    headers = { 'Accept': 'application/json',
                'Authorization': 'token ' + accesstoken
                }

    # Get User Repos
    repos = get_all(github_url_user_repos, headers=headers)

    # Get User's Org Repos
    orgs = get_orgs(headers=headers)
    for org in orgs:
        # Get User's Repo for each Org
        org_repos = get_all(github_url_org_repos.replace(':org', org['login']), headers=headers, max=100)
        org_repos.sort(key=lambda x:x['full_name'])
        org['repos'] = org_repos

    # Get all Public repos
    all_repos = get_public_repos(headers=headers)

    return render_template('index.html', user_repos = repos, org_repos = orgs, all_repos = all_repos)

@app.route('/login')
def login():
    return render_template('login.html')



@app.route('/authorize')
def authorize():
    session['github_state'] = os.urandom(24).encode('hex')
    params = {  'client_id':github_clientid,
                'scope':'user,repo,public_repo,gist,read:org',
                'state':session['github_state']
                }
    uri = github_url_auth + "?" + urlencode(params);
    return redirect(uri)


@app.route('/access')
def access():
    code = request.args.get('code', None)
    state = request.args.get('state', None)
    if not code or ('github_state' in session and state != session['github_state']):
        return redirect(url_for('.index'))

    headers = { 'Accept': 'application/json' }
    params = {  'client_id':github_clientid,
                'client_secret':github_secretid,
                'code':code,
                'state':session['github_state']
                }
    resp = requests.post(github_url_access_token, params=params, headers=headers, verify=False)

    if resp.status_code != requests.codes.ok:
        return redirect(url_for('.index'))

    json = resp.json()
    session['github_accesstoken'] = json['access_token']
    return redirect(url_for('.index'))
