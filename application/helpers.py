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
#
#######################################################################


def urlsafe_key(key):
    """
    converts a ndb key into urlsafe key, wrapper over ndb.urlsafe
    """
    try:
        return key.urlsafe()
    except:
        return key


def convert_entity_to_dict(entity,
                           with_key=False):
    """
    converts entity to json-able dict
    """
    errors = []
    entity_dict = {}

    try:
        if isinstance(entity, dict):
            entity_dict = entity
        else:
            entity_dict = entity.to_dict()

        if with_key:
            try:
                entity_dict['key'] = entity.key.urlsafe()
                if entity_dict['quoted_tweet']:
                    entity_dict['quoted_tweet'] = entity_dict[
                            'quoted_tweet'].urlsafe()
            except Exception as e:
                print '\n\n\n\n\n Err ' + e
                pass

    except Exception as e:
        errors.append('entity - Unexpected Error - {0}'.format(e))

    if errors:
        return {'errors': errors}
    else:
        return entity_dict


def convert_tweet_to_dict(tweet):
    """
    convert tweet to dict and as per requirements
    """
    data = convert_entity_to_dict(tweet)
    try:
        # add additonal data,
        data.update({
            "id": data["tweet_id"],
            "date": data["created_at"].strftime('%Y-%m-%dT%H:%M:%SZ'),
            "type": "twitter",
            "quoted_tweet": None,
        })

        if tweet.quoted_tweet_entity:
            data['quoted_tweet'] = convert_tweet_to_dict(
                    tweet.quoted_tweet_entity)
    except:
        pass

    return data


def convert_twitter_user_to_dict(user):
    """
    convert tweet user to dict and as per requirements
    """
    data = convert_entity_to_dict(user)
    try:
        # add additonal data,
        data.update({
            "id": data["id_str"],
            "type": "user",
        })
    except:
        pass

    return data
