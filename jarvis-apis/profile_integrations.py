from models import User, TrelloCredentials
from config import validateToken
import json


def listIntgerations(data):
    tokenValidator = validateToken(data["token"])
    if not tokenValidator[0]:
        return tokenValidator[1]
    return {
        "statusCode":200,
        "users": json.loads(tokenValidator[1].to_json())
    }

def createIntegrations(data):
    tokenValidator = validateToken(data["token"])
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
    if data.get("jenkins", False):
        pass


def updateIntegrations(data):
    return createIntegrations(data)