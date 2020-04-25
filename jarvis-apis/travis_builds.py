from config import validateToken
import json
import requests
from dateutil.parser import parse
from datetime import datetime, timezone

def timebuilder(val):
    val = int(val)
    if val < 100:
        return val, "seconds"
    elif val < 3600:
        return val//60, "minutes"
    elif val < 86400:
        return val//3600, "hours"
    else:
        val = val//86400
    if val < 60:
        return val, "days"
    else:
        return val//30, "months"

def buildResult(token, projectname):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    org_name = data["github_creds"]["org_name"]
    travis_endpoint = "https://api.travis-ci.org/repos/{}/{}/builds"
    travis_endpoint = travis_endpoint.format(org_name, projectname)
    resp = requests.get(travis_endpoint)
    if resp.status_code != 200:
        return {
            "statusCode": 301,
            "message": "Build Status Failed to Fetch. Please chek to see if your repo is private or not?"
        }
    resp = resp.json()
    if len(resp) < 1:
        return {
            "statusCode": 301,
            "message": "Jarvis Failed to Find a Build for this project. Have you setup travis ci correctly for this repository?"
        }
    message_builder = "Total Number of builds run for this project are {}. "
    message_builder = message_builder.format(len(resp))
    message_builder += "Total build time of all the builds is {} {}"
    a, b = timebuilder(sum([i["duration"] for i in resp]))
    message_builder = message_builder.format(a, b)
    first_item = resp[0] 
    message_builder += "The latest build was started at {} ."
    message_builder = message_builder.format(
        parse(first_item["started_at"]).strftime("%I:%M %p %d %B, %Y")
    )
    if first_item["state"] == "finished":
        message_builder += "It finished {} {} ago with status as"
        a, b = timebuilder(
            (
                datetime.now(timezone.utc) - parse(first_item["started_at"])
            ).seconds
        )
        message_builder = message_builder.format(a, b)
        badge_url = "https://api.travis-ci.org/{}/{}.svg?branch={}"
        resp = requests.get(
            badge_url.format(org_name,projectname,first_item["branch"])
        )
        if a.text.find("passing") != -1:
            message_builder += " build passed. "
        elif a.text.find("failing") != -1:
            message_builder += " build failed. "
        else:
            message_builder += " build invalid. "


    message_builder += "This build was triggered in response to {} with commit message {} on branch {}."
    message_builder = message_builder.format(
        first_item["event_type"],
        first_item["message"].lower()[:100],
        first_item["branch"]
    )

