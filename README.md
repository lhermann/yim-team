A) Create new python executable
===============================
1. Get Python 3: https://www.python.org/downloads/
2. Create a new virtual environment: `python3 -m venv ~/venv/MP1.11`
3. Activate it: `source ~/venv/MP1.11/bin/activate`

MP = My Project, 1.11 = Django 1.11

More info: https://docs.python.org/3.6/library/venv.html

B) Install apps
===============
`pip install -r requirements.txt`

C) Create config file
=====================
Save this as `config.ini` in your directory above the git repo and adjust the database values (you can leave the rest as it is):

```
[database]
USER:
PASSWORD:
HOST:
PORT:
ENGINE: django.db.backends.sqlite3
NAME: ~/django/yimteam/db.sqlite3

[secrets]
SECRET_KEY: 9ab*f-nj)80la)v2(n^@_%@(zewe-$^emmnldfk#fbt32x*)§9
QUERY_API_KEYS: test1234567890
SENTRY_DSN:

[addresses]
ALLOWED_HOSTS: 
QUERY_WHITE_LIST: 127.0.0.1

[debug]
DEBUG: true

[email]
DEFAULT_FROM_EMAIL:
HOST:
HOST_PASSWORD:
HOST_USER:
```

D) Migration
============
`cd` into the base dir (git) and run `python3 manage.py migrate` in order to update your database

E) Start the dev server
=======================
Run `python3 manage.py runserver`

That's it!
