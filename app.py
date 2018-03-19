from flask import Flask, jsonify
from flask_restful import Resource, Api
from webargs import fields
from webargs.flaskparser import use_kwargs
from dotenv import load_dotenv, find_dotenv
import requests
from os import environ as env
import urllib.parse
from jose import jwt


env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)

domain = env.get("DOMAIN")
audience = env.get("AUDIENCE")
management_audience = env.get("MANAGEMENT_AUDIENCE")
client_secret = env.get("CLIENT_SECRET")
client_id = env.get("CLIENT_ID")
connection = env.get("CONNECTION")
redirect_uri = env.get("REDIRECT_URI")

algorithms = ["RS256"]


def custom_response(status_code, message):
    """Return serialized custom response."""
    response = jsonify({'message': message})
    response.status_code = status_code
    return response


class Provider:
    """A class for working with backend auth0 provider."""

    _headers = {'content-type': 'application/json'}

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
        r = requests.post(
            self.oauth_token_url, json=data, headers=self._headers
        )
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

    def decode_token(self, token):
        url = f'https://{self.domain}/.well-known/jwks.json'
        resp = requests.get(url)
        jwks = resp.json()

        try:
            unverified_header = jwt.get_unverified_header(token)
            if unverified_header['alg'] == 'HS256':
                raise jwt.JWTError()
        except jwt.JWTError:
            return custom_response(
                401, 'Use an RS256 signed JWT Access Token.'
            )

        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'], 'kid': key['kid'], 'use': key['use'],
                    'n': key['n'], 'e': key['e']
                }

        try:
            payload = jwt.decode(
                token, rsa_key, algorithms=algorithms, audience=client_id,
                issuer=f'https://{self.domain}/'
            )
        except jwt.ExpiredSignatureError:
            return custom_response(401, 'Token expired.')
        except jwt.JWTClaimsError:
            return custom_response(401, 'Invalid Claims')
        else:
            return payload


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


class Login(Resource):
    def get(self):
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'scope': 'openid profile',
            'redirect_uri': redirect_uri
        }
        authorize_url = f'https://{domain}/authorize?'
        redirect_url = '{0}{1}'.format(authorize_url,
                                       urllib.parse.urlencode(params))
        return ({}, 201, {'Location': redirect_url})


class Callback(Resource):

    provider = Provider(
        client_id, client_secret, management_audience, domain
    )
    url = f'https://{domain}/oauth/token'

    @use_kwargs({
        'code': fields.String(required=True),
    })
    def get(self, code):
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }
        resp = self.provider.post(self.url, data)
        id_token = resp.json()['id_token']
        return self.provider.decode_token(id_token)


app = Flask(__name__)
api = Api(app)
api.add_resource(User, '/user')
api.add_resource(Users, '/users')
api.add_resource(Login, '/login')
api.add_resource(Callback, '/callback')
