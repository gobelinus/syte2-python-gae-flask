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
# tasks related stuff
#
#######################################################################

###########
# imports #
###########

# -*- std imports -*-
import datetime
import xml.sax.saxutils as saxutils
# import random
import re
import logging
import json                # Python 2.7.

# -*- third party imports -*-
import dateutil.parser

from flask import (
    jsonify,
    # url_for,
)

# -*- local import -*-
from application.twoauth import TwitterOAuth10
from application import (
    app,
)

from application.models import (
    add_tweet,
    get_user_preferences,
    get_user_info,
    update_user_preferences,
    Picture,
    User,
    UserInfo,
)


def linkify_text(text, entities):
    """
    convert urls, hashtags, mentions etc into clickable links
    """
    # remove new line char with br html element
    text = saxutils.unescape(data=text,
                             entities={'\n': '<br>'})

    # parsing links/urls with text can get tricky so using entities
    if 'urls' in entities:
        for url in entities['urls']:
            long_url = url['expanded_url']
            display_url = (url['display_url']
                           if 'display_url' in url
                           else long_url)
            urlele = (u'<a href="{0}"'.format(long_url) +
                      u' target="_blank">{0}</a>'.format(display_url))
            short_url = url['url']
            text = text.replace(short_url, urlele)

    # linkify mentions with urls
    mention_ele = ('<a href="https://twitter.com/\g<mention>" ' +
                   'target="_blank">@\g<mention></a>')
    text = re.sub('(^|)@(?P<mention>(\w+))', mention_ele, text,
                  flags=re.IGNORECASE | re.UNICODE)

    # linkify hashtags
    hash_ele = ('<a href="https://twitter.com/search?q=' +
                '%23\g<hash>" target="_blank">#\g<hash></a>')
    text = re.sub('(^|)#(?P<hash>(\w+))', hash_ele, text,
                  flags=re.IGNORECASE | re.UNICODE)

    return text


def parse_tweet(status):
    """
    parse a tweet json and returns a dict containing keys for adding tweet
    to db
    """
    try:
        pictures = []
        tweet = {
            'tweet_id': status['id_str'],
        }

        entities = status['entities'] if 'entities' in status else {}

        try:
            message = status['full_text'] or status['text']
        except:
            message = status['text']

        message = linkify_text(message, entities)

        try:
            created_at = status['created_at']
            created_at = dateutil.parser.parse(created_at,
                                               ignoretz=True)
        except Exception as e:
            logging.error('200 - Exception while ' +
                          'parsing date - {0}'.format(e))
            created_at = datetime.datetime.utcnow()

        if ('extended_entities' in status and
                status['extended_entities'] and
                'media' in status['extended_entities']):
            for media in status['extended_entities']['media']:
                picture = {
                    'id_str': media['id_str'],
                    'url': media['media_url_https'],
                    'tweet_id': tweet['tweet_id']
                }

                if (media['sizes'] and media['sizes']['small']):
                    picture['width'] = media['sizes']['small']['w']
                    picture['height'] = media['sizes']['small']['h']

                pictures.append(Picture(**picture))

                if ('video_info' in media and
                        'variants' in media['video_info']):
                    for video in media['video_info']['variants']:
                        if ('content_type' in video and
                                video['content_type'] == 'video/mp4'):
                            tweet['video'] = video['url']

            tweet['pictures'] = pictures

        try:
            retweeted_status = status['retweeted_status']
        except:
            retweeted_status = None

        post = retweeted_status or status
        tweet_url = 'https://www.twitter.com/{}/status/{}'

        tweet.update({
            'created_at': created_at,
            'text': message,
            'url': tweet_url.format(post['user']['screen_name'],
                                    post['id_str']),
            'favorites': post['favorite_count'],
            'retweets': post['retweet_count'],
            'user': User(username=post['user']['screen_name'],
                         name=post['user']['name'],
                         picture=post['user']['profile_image_url_https'],
                         id_str=post['user']['id_str'])
        })

        if (retweeted_status):
            try:
                original_text = (retweeted_status['full_text'] or
                                 retweeted_status['text'])
            except:
                original_text = retweeted_status['text']

            retweet_entities = (retweeted_status['entities']
                                if 'entities' in retweeted_status
                                else {})
            tweet['original_text'] = linkify_text(original_text,
                                                  retweet_entities)

        try:
            if 'quoted_status' in status and status['quoted_status']:
                quoted_tweet = parse_tweet(status['quoted_status'])
                tweet['quoted_tweet'] = add_tweet(**quoted_tweet)
        except:
            pass

        return {
            'tweet': tweet,
            'pictures': ([] if retweeted_status else pictures)
        }

    except Exception as e:
        logging.error('500 - Error while parsing status ' +
                      '- {0} - {1}'.format('status', e))
        pass


def fetch_tweets():
    """
    fetches tweets from twitter
    """
    # get last_tweet from user prefs
    last_tweet_id = ''
    user_pictures = []
    update_user = False
    user_info_db = None

    try:
        user_id = (app.config['USER_KEY'])
        user_prefs = get_user_preferences(user_id=user_id)
        last_tweet_id = user_prefs.last_tweet

        user_info_db = get_user_info(user_id=user_id)
        user_pictures = user_info_db.pictures
    except Exception as e:
        logging.error('user info {0}'.format(e))
        pass

    if not user_info_db:
        user_info_db = UserInfo(user_id=user_id)

    # global tw oauth wrapper
    tw_oauth = TwitterOAuth10()

    timeline = tw_oauth.get_user_timeline(last_tweet=last_tweet_id)

    try:
        statuses = json.loads(timeline)
        # statuses = statuses[0:1]
    except Exception as e:
        logging.error('Exception while loading timeline - {0}'.format(e))
        try:
            statuses = json.loads(timeline.encode('utf-8'))
            pass
        except:
            statuses = None

    if statuses:
        statuses.reverse()

    # logging.info(statuses)
    for index, status in enumerate(statuses):
        tweet_data = parse_tweet(status)
        logging.info('index = {0}, tweet = {1}, pictures = {2}'.format(
            index, 'tweet' in tweet_data, 'pictures' in tweet_data))

        if tweet_data:
            if 'tweet' in tweet_data and tweet_data['tweet']:
                add_tweet(**tweet_data['tweet'])

            if 'pictures' in tweet_data:
                pictures = tweet_data['pictures']
                if pictures:
                    user_pictures.extend(pictures)
                    update_user = True
                    # make user_pictures by unique values of id_str
                    # ref: https://stackoverflow.com/a/11092590
                    user_pictures = {v.id_str: v
                                     for v in user_pictures}.values()

            # get latest user info
            # logging.info(index)
            if index == 0:
                try:
                    user_info_db.id_str = status['user']['id_str']
                    user_info_db.name = status['user']['name']
                    user_info_db.username = status['user']['screen_name']
                    user_info_db.url = status['user']['url']
                    user_info_db.followers = status['user']['followers_count']
                    user_info_db.following = status['user']['friends_count']
                    user_info_db.statuses = status['user']['statuses_count']
                    user_info_db.picture = status['user']['profile_image_url']

                    try:
                        if (status['user']['desciption']):
                            user_info_db.description = linkify_text(status[
                                'user']['desciption'], {})
                    except:
                        pass

                    try:
                        if (status['user']['location'] and
                                len(status['user']['location']) > 0):
                            user_info_db.location = status['user']['location']
                    except:
                        pass

                    try:
                        if status['user']['profile_image_url_https']:
                            user_info_db.picture = (status['user'][
                                    'profile_image_url_https'].replace(
                                        '_normal', ''))
                    except:
                        pass

                    try:
                        if status['user']['profile_banner_url']:
                            user_info_db.banner = (
                                    status['user']['profile_banner_url'] +
                                    '/mobile_retina')
                    except:
                        pass

                    # logging.info(user_info)
                    update_user = True
                except Exception as e:
                    logging.debug('user info - {0}'.format(e))

    if update_user:
        # logging.info('\n\n\n================\nupdating user')
        # update_user_info(user_id, user_info)
        if user_pictures:
            try:
                user_pictures.reverse()
                user_info_db.pictures = user_pictures
            except Exception as e:
                logging.info('pic - {0}'.format(e))
        user_info_db.put()

    try:
        last_tweet_id = statuses[-1]['id_str']
    except Exception as e:
        logging.debug('last tweet id - {0}'.format(e))
        last_tweet_id = -100

    if last_tweet_id:
        logging.info('last_tweet_id = {}'.format(last_tweet_id))
        update_user_preferences(user_id=user_id,
                                last_tweet_id=last_tweet_id)
        pass


def process_tweet_tasks():
    """
    process tweet tasks
    """
    logging.info('Welcome to processing')
    try:
        fetch_tweets()
    except Exception as e:
        logging.info('Error while processing - {0}'.format(e))
        pass

    return jsonify(succes=1)
