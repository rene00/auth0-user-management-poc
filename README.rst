What?
=====

A proof-of-concept user management microservice backed by `auth0 <https://auth0.com>`_.

Why?
====

I've taken a deep dive into auth0 which is a service which offers authentication, authorization and identity management. The service is heavily driven by API which I wanted to learn.

I decided to build a proof of concept microservice which I could use in the future to hand off user management for future projects I work on. The idea is that this microservice would be backed by auth0 and sit behind a firewall. A consumer of the microservice could be a frontend web application which has no idea about the backend identity and authentication service. The frontend web application only needs to hit internal endpoints to handle basic user management actions such as creating a new user and authenticating an existing user. All state is held within auth0.com.

How?
====

The microservice is written in python and uses flask-restful. It's only a very early proof-of-concept at the moment so there are a few issues which I'll fix in a later version:

  - No authentication required. The idea is that the service can only be accessed internally.
  - Blocking API calls to the backend service. The service will block the frontend client whilst calling out to the backend auth0 service.
  - Lacking other other useful actions such as password reset and user account information updates.

Going forward, I will most likely implement:

  - Use auth0.com to manage user metadata.
  - Implement MFA.
  - Support social logins.

Install and Run
===============

You can run this microservice by building a virtualenv and running flask::

  $ mkvirtualenv --python=`which python3` auth0-user-management-poc
  $ git clone https://github.com/rene00/auth0-user-management-poc.git
  $ cd auth0-user-management-poc
  $ pip3 install -r requirements.txt

You will need to create a ```.env``` file::

  DOMAIN=example.au.auth0.com
  CLIENT_ID=YOUR_AUTH0_CLIENT_ID
  CLIENT_SECRET=YOUR_AUTH0_CLIENT_SECRET
  AUDIENCE=YOUR_AUTH0_AUDIENCE
  MANAGEMENT_AUDIENCE=https://example.au.auth0.com/api/v2/
  CONNECTION=Username-Password-Authentication
  REDIRECT_URI=http://localhost:5000/callback

Then to run::

  $ FLASK_APP=app.py flask run
