#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################
#                                   _           _____
#                                  / |_        / ___ `.
#  _ .--.   _   __  .--.    _   __`| |-'.---. |_/___) |
# [ '/'`\ \[ \ [  ]( (`\]  [ \ [  ]| | / /__\\ .'____.'
# | \__/ | \ '/ /  `'.'.   \ '/ / | |,| \__.,/ /_____
# | ;.__/[\_:  /  [\__) )[\_:  /  \__/ '.__.'|_______|
# [__|     \__.'           \__.'
#
# urls related stuff

# add task via cron. run main logic as task as tasks have a better dealine
# than the normal url request
#
#######################################################################

###########
# imports #
###########

# -*- std imports -*-

# -*- third party imports -*-
from flask import render_template

# -*- local import -*-
from application import (
    app,
    tasks,
    views,
)
from application.constants import (
    POST_ONLY,
)


# URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/
# appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Home page
app.add_url_rule('/', 'home', view_func=views.home)

# url to add twitter task
app.add_url_rule('/admin/tweet/fetch', 'fetch_tweets',
                 view_func=views.fetch_tweets)

# task to fetch tweet from twitter
app.add_url_rule('/admin/task/tweet-fetch',
                 'task_fetch_tweets',
                 view_func=tasks.process_tweet_tasks,
                 methods=POST_ONLY,
                 )


# Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
