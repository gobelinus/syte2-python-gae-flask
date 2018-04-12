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
from operator import itemgetter

# -*- third party imports -*-
from flask import (
    jsonify,
    make_response,
    url_for,
)
from google.appengine.api import (
    taskqueue,
    memcache,
)

# -*- local import -*-
from application import (
    app,
    constants,
)
from application.helpers import (
    convert_tweet_to_dict,
    convert_twitter_user_to_dict,
    urlsafe_key,
)
from application.models import (
    grab_tweets,
    Tweet,
    get_user_info,
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


def get_twitter_data(page=0):
    """
    get twitter stream
    """
    # get cursor data from memcache
    cursors = memcache.get(constants.API_KEY_CURSORS)
    if not cursors:
        cursors = {}
    cursor_page = str(page)
    if (cursors and
            cursor_page in cursors and
            constants.API_KEY_TWITTER in cursors[cursor_page]):
        twitter_cursor = cursors[cursor_page][constants.API_KEY_TWITTER]
    else:
        twitter_cursor = None

    (tweets, cursor, has_more) = grab_tweets(sortby=-Tweet.created_at,
                                             start_cursor=twitter_cursor)

    ret_val = map(convert_tweet_to_dict, tweets)
    # update cursor to cache
    next_page = str(int(page) + 1)
    if next_page not in cursors:
        cursors[next_page] = {}
    cursors[next_page][constants.API_KEY_TWITTER] = urlsafe_key(cursor)

    # update cache
    memcache.set(constants.API_KEY_CURSORS, cursors,
                 time=constants.CACHE_TIME_DAY)

    return ret_val


def get_twitter_user():
    """
    return twitter user
    """
    user_id = (app.config['USER_KEY'])
    user_info = get_user_info(user_id=user_id)
    ret_val = convert_twitter_user_to_dict(user_info)
    return make_response(jsonify(ret_val), 200)


def get_twitter_stream(page=0):
    """
    get twitter stream
    """
    ret_val = get_twitter_data(page=page)
    return make_response(jsonify(ret_val), 200)


def get_stream(page=0):
    """
    get user stream
    """
    ret_val = get_twitter_data(page=page) or []

    # sort data by reverse chronologically
    ret_val = sorted(ret_val, key=itemgetter("date"), reverse=True)
    return make_response(jsonify(ret_val), 200)
