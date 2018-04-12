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
# constants for app
#
#######################################################################


# request methods
HTTP_REQUEST_GET = 'GET'
HTTP_REQUEST_POST = 'POST'

# request methods allowed
POST_ONLY = [HTTP_REQUEST_POST]

# taskqueues related constants
QUEUE_NAME_DEFAULT = 'default'
QUEUE_NAME_TIMELINE = 'timeline'

# batch sizes and pagination stuff
TWEETS_PER_PAGE = 20

# caching
CACHE_TIME_DAY = 24 * 60 * 60  # 1 day

# keys
API_KEY_CURSORS = 'cursors'
API_KEY_TWITTER = 'twitter'
