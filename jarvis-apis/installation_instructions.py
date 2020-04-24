from config import validateToken
import json
import base64
import requests
import markdown2
from bs4 import BeautifulSoup


def listgitrepos(token):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    username = data["github_creds"]["git_username"]
    personal_token = data["github_creds"]["git_personal_token"]
    org_name = data["github_creds"]["org_name"]
    url = "https://api.github.com/orgs/{}/repos".format(org_name)
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
    

def helpwithinstallation(token, reqdata):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    projectname = reqdata["projectname"]
    needDocker = reqdata["docker"]
    if not needDocker:
        OS = reqdata["os"]
    else:
        OS = "Ubuntu"
    url = "https://raw.githubusercontent.com/{}/{}/master/README.md".format(
        org_name, projectname
    )
    resp = requests.get(url).text
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
    if not needDocker:
        return {
            "statusCode": 200,
            "message": instrSet.get(
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
    return {
        "statusCode": 200, 
        "message": """
                A docker file with relevant instructions has been\
                compiled and sent to your email, please read it and\
                use docker to run the file on your server.
            """
    }
