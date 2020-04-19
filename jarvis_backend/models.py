from mongoengine import Document, StringField, EmailField, URLField, BinaryField


class User(Document):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    company_name = StringField(required=True)
    company_url =  URLField(required=True, unique=True)
    password =  StringField(required=True)
    github_url = StringField(required=True, default="")
    confluence_url = StringField(required=True, default="")
    jenkins_url = StringField(required=True, default="")
    confluence_url = StringField(required=True, default="")
    trello_url = StringField(required=True, default="")