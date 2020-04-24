from models import User
import jwt
import json

def validateToken(token):
    try:
        decoded_token = jwt.decode(
            token,
            "YOUR-KEY-GOES-HERE"
        )["email"]
        user = User.objects.get(email=decoded_token)
        return True, user
    except:
        return False, {
            'statusCode': 401,
            "message": "InvalidCredentials"
        }