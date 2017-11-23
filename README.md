Create new python executable
===============================
1. Get Python 3: https://www.python.org/downloads/
2. Create a new virtual environment: `python3 -m venv ~/venv/MP1.11`
3. Activate it: `source ~/venv/MP1.11/bin/activate`

MP = My Project, 1.11 = Django 1.11

More info: https://docs.python.org/3.6/library/venv.html

Install apps
===============
`pip install -r requirements.txt`

Create config file
=====================
Copy `config.example.ini` as `config.ini` and adjust the database values

Migration
============
`cd` into the base dir (git) and run `npm run migrate` in order to update your database

Start the dev server
=======================
Run `npm run dev`

Log in as:

    user: admin
    password: admin

That's it!
