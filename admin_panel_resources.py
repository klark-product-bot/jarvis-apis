import json
import jwt
from datetime import datetime, timedelta
import mongoengine
import bcrypt
import os
from models import User

def lambda_handler(event, context):
    data = json.loads(event["body"])
    mongoengine.connect(
        'Users',
        host=os.environ("dbipaddress"),
        username=os.environ("dbusername"), 
        password=os.environ("dbpassword"), 
        authentication_source='admin'
    )
    user = User(
        name = data["username"],
        email = data["email"],
        company_name = data["company_name"],
        company_url =  data["company_url"],
        password =  bcrypt.hashpw(data["password"], bcrypt.gensalt())
    )
    try:
        user.save()
        return {
            'statusCode': 200,
            'body': json.dumps(
                {
                    "message": "SignupSuccessful",
                    "token": jwt.encode({
                        'email': data["email"],
                        'expiry_date': datetime.now()+timedelta(hours=24)
                    }, os.environ("jwtsecret"))
                }
            )
        }
    except:
        return {
            'statusCode': 301,
            'body': json.dumps({"message": "SignupFailed"})
        }
