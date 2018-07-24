Create new Python executable and install Python packages
===============================
`pipenv sync`

Create config file
=====================
Copy `config.example.ini` as `config.ini` and adjust the database values

Development
=======================
Migrate: `npm run migrate`

Start dev server: `npm run dev`

Log in as:

    user: admin
    password: admin

Deployment
==========

`push` to the server repo.

To be able to do that it needs a litte preparation.

If you want to push to GitHub and the server the same time you can do:

```bash
git remote set-url origin --push --add https://github.com/lhermann/yim-team.git
git remote set-url origin --push --add ssh://<username>@<host>:<port><home_dir>/git/yimteam.git (I can send you the concrete address if you like)
```

I've read that you have to fetch/pull in case somebody else changed something. …We will see.

More information at [stackoverflow](https://stackoverflow.com/questions/849308/pull-push-from-multiple-remote-locations) and [git-scm](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes).

Git `post-receive` hook
=======================

(Just to have this documented somewhere in case it gets lost.)

To make this deployment possilbe these lines are necessary in `post-receive`:

```bash
#!/bin/sh
PROJECT="yimteam"
WORK_TREE=$HOME/django-projects/$PROJECT
GIT_DIR=$HOME/git/$PROJECT.git
git --work-tree=$WORK_TREE --git-dir=$GIT_DIR checkout -f
cd $WORK_TREE && git --work-tree=$WORK_TREE --git-dir=$GIT_DIR submodule update --init
python3 $WORK_TREE/django-up-to-date/build.py
touch $HOME/django-projects/yimteam_uwsgi.ini
```
