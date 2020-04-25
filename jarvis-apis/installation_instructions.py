from config import validateToken
import json
import base64
import requests
import markdown2
from bs4 import BeautifulSoup
# from os import environ

def githubCredBuilder(userdata):
    username = userdata["github_creds"]["git_username"]
    personal_token = userdata["github_creds"]["git_personal_token"]
    base64string = base64.encodestring('{}/token:{}'.format(username, personal_token).encode()).decode().replace("\n", "")
    return {"Authorization": "Basic "+base64string}


def featureDevelopmentSummary(token, projectname, issuename):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    github_creds = githubCredBuilder(data)
    issues_url = "https://api.github.com/repos/{}/{}/issues?state=all"
    issues_url.format(org_name, projectname)
    github_creds = githubCredBuilder(data)
    resp = requests.get(issues_url, headers=github_creds)
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "message": "Issues Request Failed"
        }
    issueNumber = 1
    for i in resp.json():
        if i["name"].lower() == issuename.lower():
            issueNumber = i["number"]
    timeline_url = "https://api.github.com/repos/{}/{}/issues/{}/timeline"
    timeline_url.format(org_name, projectname, issueNumber)
    github_creds["Accept"] = "application/vnd.github.mockingbird-preview","description":""}
    resp = requests.get(timeline_url, headers=github_creds)
    


def projectreleasestatus(token, projectname):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    milestone_url = "https://api.github.com/repos/{}/{}/milestones?sort=due_on"
    milestone_url = milestone_url.format(org_name, projectname)
    github_creds = githubCredBuilder(data)
    resp = requests.get(milestone_url, headers=github_creds)
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": resp.json(),
            "message": "Milestone Request Failed"
        }
    if len(resp)<1:
    resp = resp.json()
        return {
            "statusCode": 301,
            "message": "No Milestone Found"
        }
    milestone = resp[0]
    issues_url = "https://api.github.com/repos/{}/{}/issues?state=all&labels=urgent&milestone={}"
    issues_url = issues_url.format(org_name, projectname, milestone["number"])
    resp = requests.get(issues_url, headers=github_creds)
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": resp.json(),
            "message": "Milestone Request Failed"
        }
    milestone["urgent_issues"] = resp.json()
    return {
        "statusCode":200,
        "milestone": milestone
    }


def listgitrepos(token):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    url = "https://api.github.com/orgs/{}/repos".format(org_name)
    resp = requests.get(url, headers=githubCredBuilder(data))
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "reason": resp.json(),
            "message": "Repository Request Failed"
        }
    else:
        data = resp.json()
        reponames = []
        for i in data:
            reponames.append({"name": i["name"]}) 
        data = {
            "statusCode": 200,
            "data": reponames
        }
        return data
    

def helpwithinstallation(token, projectname, needDocker=False, OS="ubuntu"):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    url = "https://raw.githubusercontent.com/{}/{}/master/README.md".format(
        org_name, projectname
    )
    resp = requests.get(url)
    if resp.status_code != 200:
        return {
            "statusCode": 200, 
            "message": "I am extremely sorry but no installation instructions were found on your repository. You are on your own for this one."
        }
    resp = resp.text
    soup = BeautifulSoup(
        markdown2.markdown(resp), 
        "html.parser"
    )
    instrSet = {}
    for i in soup.find_all("code"):
        instructions = i.get_text()
        print(instructions, type(instructions))
        if instructions[0:4] == "bash":
            if instructions.find("apt") != -1:
                instrSet["ubuntu"] = instructions[5:].strip().split("\n")
            elif instructions.find("yum"):
                instrSet["redhat"] = instructions[5:].strip().split("\n")
        elif instructions[0:6] == "shell":
            instrSet["windows"] = instructions[7:].strip().split("\n")
        else:
            instrSet["macos"] = instructions[7:].strip().split("\n")
    if instrSet == {}:
        return {
            "statusCode": 200, 
            "message": "I am extremely sorry but no installation instructions were found on your repository. You are on your own for this one."
        }
    if not needDocker:
        return {
            "statusCode": 200,
            "instructions": instrSet.get(
                OS, 
                "Sorry this software doesn't install on your OS"
            )
        }
    dockerFile = """
        # Pull base image.
        FROM ubuntu:18.04

        # Install.
        RUN \
        sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
        apt-get update && \
        apt-get -y upgrade && \
        apt-get install -y build-essential && \
        apt-get install -y software-properties-common && \
        apt-get install -y byobu curl git htop man unzip vim wget && \
        rm -rf /var/lib/apt/lists/* && \ {}

        # Add files.
        ADD root/.bashrc /root/.bashrc
        ADD root/.gitconfig /root/.gitconfig
        ADD root/.scripts /root/.scripts

        # Set environment variables.
        ENV HOME /root

        # Define working directory.
        WORKDIR /root

        # Define default command.
        CMD ["bash"]
    """.format("&&\\\n".join(i for i in instrSet["ubuntu"]))
    return mailInstallationInstructions(dockerFile,data["email"])

def mailInstallationInstructions(dataToMail, email):
    # TODO Actually send the mail
    # email_username = environ.get('username')
    # email_password = environ.get('password')
    return {
        "statusCode": 200, 
        "message": "A docker file with relevant instructions has been compiled and sent to your email, please read it and use docker to run the file on your server."
    }   