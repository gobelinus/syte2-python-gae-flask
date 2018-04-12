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
# settings.py

# Configuration for Flask app

# Important: Place your keys in the secret_keys.py module,
#   which should be kept out of version control.
#
#######################################################################

###########
# imports #
###########

# -*- local import -*-
from secret_keys import (
    CSRF_SECRET_KEY,
    SESSION_KEY,
    USER_KEY,
    TW_CONSUMER_KEY,
    TW_CONSUMER_SECRET,
    TW_TOKEN,
    TW_TOKEN_SECRET,
)


class Config(object):
    # Set secret keys for CSRF protection
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY
    USER_KEY = USER_KEY
    TW_CONSUMER_KEY = TW_CONSUMER_KEY
    TW_CONSUMER_SECRET = TW_CONSUMER_SECRET
    TW_TOKEN = TW_TOKEN
    TW_TOKEN_SECRET = TW_TOKEN_SECRET


class Development(Config):
    DEBUG = True
    # Flask-DebugToolbar settings
    DEBUG_TB_PROFILER_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False


class Testing(Config):
    TESTING = True
    DEBUG = True
    CSRF_ENABLED = True


class Production(Config):
    DEBUG = False
    CSRF_ENABLED = True
