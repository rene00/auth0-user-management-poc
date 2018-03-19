from flask import Flask, jsonify
from flask_restful import Resource, Api
from webargs import fields
from webargs.flaskparser import use_kwargs
from dotenv import load_dotenv, find_dotenv
import requests
from os import environ as env


env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)
domain = env.get("DOMAIN")
management_audience = env.get("MANAGEMENT_AUDIENCE")
client_secret = env.get("CLIENT_SECRET")
client_id = env.get("CLIENT_ID")
connection = env.get("CONNECTION")
algorithms = ["RS256"]

HEADERS = {'content-type': 'application/json'}


def custom_response(status_code, message):
    """Return serialized custom response."""
    response = jsonify({'message': message})
    response.status_code = status_code
    return response


class Provider:

    def __init__(self, client_id, client_secret, management_audience, domain):
        self.client_id = client_id
        self.client_secret = client_secret
        self.management_audience = management_audience
        self.domain = domain

    @property
    def oauth_token_url(self):
        return f'https://{self.domain}/oauth/token'

    @property
    def access_token(self):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': self.management_audience,
            'grant_type': 'client_credentials',
        }
        r = requests.post(self.oauth_token_url, json=data, headers=HEADERS)
        resp = r.json()
        return resp['access_token']

    @property
    def headers(self):
        return {
            'content-type': 'application/json',
            'authorization': f'Bearer {self.access_token}'
        }

    def get(self, url, params={}):
        return requests.get(url, params=params, headers=self.headers)

    def post(self, url, data):
        return requests.post(url, json=data, headers=self.headers)

    def delete(self, url, params={}):
        return requests.delete(url, params=params, headers=self.headers)


class User(Resource):

    @use_kwargs({
        'email': fields.Email(required=True)
    })
    def get(self, email):
        provider = Provider(
            client_id, client_secret, management_audience, domain
        )
        url = f'https://{domain}/api/v2/users-by-email'
        params = {'email': email}
        resp = provider.get(url, params)
        return resp.json()


class Users(Resource):

    provider = Provider(
        client_id, client_secret, management_audience, domain
    )
    url = f'https://{domain}/api/v2/users'

    @use_kwargs({
        'email': fields.Email(required=True),
        'password': fields.String(required=True)
    })
    def post(self, email, password):
        data = {
            'email': email,
            'password': password,
            'connection': connection
        }
        resp = self.provider.post(self.url, data)
        return resp.json()

    def get(self):
        resp = self.provider.get(self.url)
        return resp.json()

    @use_kwargs({
        'email': fields.Email(required=True),
    })
    def delete(self, email):
        # Attempt to lookup user by email
        resp = self.provider.get(
            f'https://{domain}/api/v2/users-by-email',
            {'email': email}
        )

        try:
            user = resp.json()[0]
        except IndexError:
            return custom_response(404, 'User not found.')

        try:
            user_id = user['user_id']
        except KeyError:
            return custom_response(501, 'Failed to get user id.')

        resp = self.provider.delete(
            f'https://{domain}/api/v2/users/{user_id}'
        )
        return custom_response(resp.status_code, 'User deleted.')


app = Flask(__name__)
api = Api(app)
api.add_resource(User, '/user')
api.add_resource(Users, '/users')
