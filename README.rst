What?
=====

A proof-of-concept user management microservice backed by `auth0 <https://auth0.com>`_.

Why?
====

I've taken a deep dive into auth0 which is a service offering authentication, authorization and identity management. The service is heavily driven by API which I wanted to learn.

I decided to build a proof of concept microservice which would allow me to hand off user management for future projects I work on. The idea is that this microservice would be backed by auth0 and sit behind a firewall. A consumer of the microservice could be a front-end web application which has no idea about the back-end identity and authentication service. The front-end web application only needs to hit internal endpoints to handle basic user management operations such as creating a new user and authenticating an existing user. All state is held within auth0.com.

How?
====

The microservice is written in python and uses flask-restful. It's only a very early proof-of-concept at the moment so there are a few issues which I'll fix in a later version:

 - No front-end authentication.
 - Blocking API calls to the back-end service. The service will block the front-end client whilst calling out to the back-end auth0 service.
 - Lacking other other useful actions such as password reset and user account information updates.

Going forward, I would like to implement:

 - Manage user metadata within auth0.com.
 - Implement MFA.
 - Support social logins.
 - Email verification.

Install and Run
===============

You can run this microservice by building a virtualenv and running flask::

  $ mkvirtualenv --python=`which python3` auth0-user-management-poc
  $ git clone https://github.com/rene00/auth0-user-management-poc.git
  $ cd auth0-user-management-poc
  $ pip3 install -r requirements.txt

You will need to create a ``.env`` file::

  DOMAIN=example.au.auth0.com
  CLIENT_ID=YOUR_AUTH0_CLIENT_ID
  CLIENT_SECRET=YOUR_AUTH0_CLIENT_SECRET
  AUDIENCE=YOUR_AUTH0_AUDIENCE
  MANAGEMENT_AUDIENCE=https://example.au.auth0.com/api/v2/
  CONNECTION=Username-Password-Authentication
  REDIRECT_URI=http://localhost:5000/callback

Then to run::

  $ FLASK_APP=app.py flask run

Supported Operations
====================

List all users::

    $ http GET :5000/users

Create a new user::

    $ http POST :5000/users email=foo@example.org password=ean1nNNlErbEccud2

Delete an existing user::

    $ http DELETE :5000/users email=foo@example.org

Login as an existing user::

    $ http :5000/login

The response will include a Location header which you visit with your browser. Once authenticated with auth0 Lock, your browser will redirect to http://localhost:5000/callback which should display the account information. The idea here is that the callback URI would redirect to the frontend web application which will pass on the code to the microservice.
