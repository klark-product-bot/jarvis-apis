from config import validateToken
import json
import base64
import requests


def listgitrepos(token):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    username = data["github_creds"]["git_username"]
    personal_token = data["github_creds"]["git_personal_token"]
    org_name = data["github_creds"]["org_name"]
    url = "https://api.github.com/user/orgs/{}/repos".format(org_name)
    base64string = base64.encodestring('{}/token:{}'.format(username, personal_token).encode()).decode().replace("\n", "")
    resp = requests.get(url, headers={"Authorization": "Basic "+base64string})
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": resp.json(),
            "message": "Repository Request Failed"
        }
    else:
        data = resp.json()
        data = {
            "statusCode": 200,
            "data": data
        }
        return data
    

def helpwithinstallation(token, data):
    projectname = data["projectname"]
    needDocker = data["docker"]
    if not needDocker:
        OS = data["os"]
    else:
        OS = "Ubuntu"
