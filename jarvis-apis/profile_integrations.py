from models import User, TrelloCredentials
from config import validateToken
import json


def listIntgerations(token):
    tokenValidator = validateToken(token)
    # .only(

    # )
    if not tokenValidator[0]:
        return tokenValidator[1]
    data = json.loads(tokenValidator[1].to_json())
    data = {
        "trello_creds":data["trello_creds"],
        "travis_creds":data["travis_creds"],
        "github_url":data["github_url"],
        "confluence_url":data["confluence_url"],
        "email":data["email"]
    }
    return {
        "statusCode":200,
        "data": data
    }

def createIntegrations(token, data):
    tokenValidator = validateToken(token)
    if not tokenValidator[0]:
        return tokenValidator[1]
    if data.get("trello", False):
        trello = TrelloCredentials(
            trelloAPIkey=data["trello"]["apikey"],
            trelloAPISecret=data["trello"]["apisecret"],
            board=data["trello"]["board"]
        )
        tokenValidator[1].update(set__trello_creds=trello)
    if data.get("github", False):
        pass
    if data.get("confluence", False):
        pass
    if data.get("travis", False):
        tokenValidator[1].update(set__travis_creds=data["travis"]["apikey"])
    return {
        "statusCode":200,
        "messages": "Integrations Created/Updated Successfully"
    }   

def updateIntegrations(token, data):
    return createIntegrations(token, data)