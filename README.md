Social NEO
===========

Starting a new Django project can be a pain. Gotta get static files working, gotta 
get stuff ready for test deploys. 

Setup
-----

1. Set a new `SECRET_KEY` in `project/settings.py` (TODO: Create a new manage.py command to automate this)
2. Edit the Database settings in `.env` to best suit your needs

Create a `.env` file that will contain your settings and credentials like this:

```bash
DEPLOY='LOCAL'
PORT='8000'
DEBUG='True'
DB_ENGINE='django.db.backends.sqlite3'
DB_NAME='project_dev.sqlite'
DB_USER=''
DB_PASSWORD=''
DB_HOST=''
DB_PORT=''
FB_APP_ID='XXX'
FB_APP_SECRET='XXXX'
FB_NAMESPACE='XXX'
AWS_ACCESS_KEY_ID='XXX'
AWS_SECRET_ACCESS_KEY='XXX'
AWS_STORAGE_BUCKET_NAME='XXX'
```

Running
-------

This project comes bundled with a simple `Procfile` and `.env` so it plays nice with tools like
[Foreman](https://github.com/ddollar/foreman) or [honcho](https://github.com/nickstenning/honcho) 
out of the box. This also makes deploying to a service like [Heroku](www.heroku.com) super 
simple.

1. To start your local webserver you can:

```
foreman start
```

or

```
honcho start
```
