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
# views.py
#
# URL route handlers
#
# Note that any handler params must match the URL route params.
# For example the *say_hello* handler, handling the URL route
# '/hello/<username>' must be passed *username* as the argument.
#
#
#######################################################################

###########
# imports #
###########

# -*- std imports -*-

# -*- third party imports -*-
from flask import (
    jsonify,
    url_for,
)
from google.appengine.api import (
    taskqueue,
)

# -*- local import -*-
from application import (
    constants,
)


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html
    #Warming_Requests

    """
    return ''


# @login_required
def home():
    """home page"""
    return jsonify({'msg': 'Welcome'})


def add_task(url, queue_name=constants.QUEUE_NAME_DEFAULT,
             params={}, method=constants.HTTP_REQUEST_GET):
    """
    add a new task to taskqueue
    """
    taskqueue.add(url=url,
                  params=params,
                  queue_name=queue_name,
                  method=method)


def fetch_tweets():
    """
    add the task to fetch tweets
    """
    add_task(url=url_for('task_fetch_tweets'),
             method=constants.HTTP_REQUEST_POST,
             queue_name=constants.QUEUE_NAME_TIMELINE)
    return jsonify({'Result': 'added task'})
