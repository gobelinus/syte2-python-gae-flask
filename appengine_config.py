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
# app engine config
#
#######################################################################


# def gae_mini_profiler_should_profile_production():
#     """
#     Uncomment the first two lines to enable GAE Mini Profiler on
#     production for admin accounts
#     """
#     # from google.appengine.api import users
#     # return users.is_current_user_admin()
#     return False


# def gae_mini_profiler_should_profile_development():
#     return False


def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    return app
