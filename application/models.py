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
# models.py
#
# App Engine datastore models
#
#######################################################################

###########
# imports #
###########

# -*- std imports -*-
import logging

# -*- third party imports -*-
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

# -*- local import -*-
from application import constants


# models
class Picture(ndb.Model):
    """
    model for storing pictures
    """
    id_str = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)
    width = ndb.FloatProperty(indexed=False, default=0)
    height = ndb.FloatProperty(indexed=False, default=0)
    tweet_id = ndb.StringProperty(required=False, indexed=False)


class User(ndb.Model):
    username = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    picture = ndb.StringProperty(indexed=False)
    id_str = ndb.StringProperty(indexed=False)


class Tweet(ndb.Model):
    """
    model for storing self tweets
    """
    # twitter user id string
    tweet_id = ndb.StringProperty(indexed=True, required=True)
    url = ndb.StringProperty(indexed=False)
    text = ndb.TextProperty(indexed=False)  # actual tweet message
    retweets = ndb.IntegerProperty(indexed=False, default=0)
    favorites = ndb.IntegerProperty(indexed=False, default=0)
    original_text = ndb.TextProperty(indexed=False)

    user = ndb.StructuredProperty(User)
    created_at = ndb.DateTimeProperty(indexed=True, auto_now_add=True)

    # media
    pictures = ndb.StructuredProperty(Picture, repeated=True)
    video = ndb.StringProperty(indexed=False)

    # quoted tweet, if this tweet had any quoted tweet
    # https://docs.google.com/document/d/1AefylbadN456_Z7BZOpZEXDq8c \
    #   R8LYu7QgI7bt5V0Iw/mobilebasic
    quoted_tweet = ndb.KeyProperty(kind='Tweet')


class UserPrefs(ndb.Model):
    """
    logged in user's preferences
    """
    user_id = ndb.StringProperty()
    last_tweet = ndb.StringProperty(indexed=False)


class UserInfo(ndb.Model):
    """
    logged in user info
    """
    user_id = ndb.StringProperty()

    id_str = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    username = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)
    followers = ndb.IntegerProperty(indexed=False, default=0)
    following = ndb.IntegerProperty(indexed=False, default=0)
    statuses = ndb.IntegerProperty(indexed=False, default=0)
    picture = ndb.StringProperty(indexed=False)
    banner = ndb.StringProperty(indexed=False)

    # media
    pictures = ndb.StructuredProperty(Picture,
                                      repeated=True,
                                      indexed=False,
                                      required=False)


def get_entity_by_key_url(url_string):
    """
    Utility method to return an entity based on the key id
    """
    # ref: https://developers.google.com/appengine/docs/python/ndb/ \
    # entities#retrieving_entities
    return ndb.Key(urlsafe=url_string).get()


def get_user_preferences(user_id):
    """
    loads the user preferences of a given user
    """
    try:
        return UserPrefs.query(UserPrefs.user_id == user_id).get()
    except Exception as e:
        logging.error('mo - Exception while loading user_pref - {0}'.format(e))


def update_user_preferences(user_id, last_tweet_id):
    """
    updates the user preferences of a given user
    """
    try:
        logging.info('mo - update_user_preferences')
        user_pref = get_user_preferences(user_id)
        if not user_pref:
            user_pref = UserPrefs(user_id=user_id)
        user_pref.last_tweet = last_tweet_id
        logging.info('mo - {0}'.format(last_tweet_id))
        user_pref.put()
    except Exception as e:
        logging.error('mo - Exception while loading user_pref - {0}'.format(e))


def get_user_info(user_id):
    """
    loads the user infos of a given user
    """
    try:
        return UserInfo.query(UserInfo.user_id == user_id).get()
    except Exception as e:
        logging.error('mo - Exception while loading user_info - {0}'.format(e))


def update_user_info(user_id, user_info):
    """
    updates the user infos of a given user
    """
    try:
        # logging.info('mo - update_user_info')
        user_info_db = get_user_info(user_id)
        if not user_info_db:
            user_info_db = UserInfo(user_id=user_id, **user_info)
        else:
            # update user info to db
            for key, value in user_info.items():
                # logging.info('updating key {0} with value {1}'.format(key,
                #                                                       value))
                user_info_db._properties[key] = value
        user_info_db.put()
    except Exception as e:
        logging.error('mo - Exception while setting user_info - {0}'.format(e))


def add_tweet(**tweet_data):
    """
    """
    try:
        query = (Tweet.tweet_id == tweet_data['tweet_id'])
        tweet = Tweet.query(query).get()
        if tweet:
            return tweet.key
        else:
            tweet = Tweet(**tweet_data)
            return tweet.put()
    except:
        pass


def grab_tweets(sortby=None, start_cursor=None):
    """
    grab tweets for one page
    """
    logging.info('mo - grab_tweets')
    tweets_per_page = constants.TWEETS_PER_PAGE
    tweets = []

    query = Tweet.query()
    if sortby:
        query = query.order(sortby)

    if start_cursor:
        try:
            start_cursor = Cursor(urlsafe=start_cursor)
        except:
            start_cursor = None

    tweets, cursor, has_more = query.fetch_page(tweets_per_page,
                                                start_cursor=start_cursor)
    # fetch quoted tweet
    for t in tweets:
        if t.quoted_tweet:
            t.quoted_tweet_entity = t.quoted_tweet.get()

    return (tweets, cursor, has_more)
