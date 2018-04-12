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
# Module for implementing oauth and interacting with twitter.
#
#######################################################################

###########
# imports #
###########

# -*- std imports -*-
import base64
import hmac
import hashlib
import logging
import random
import time
import urllib

# -*- third party imports -*-
from google.appengine.api import urlfetch

# -*- local import -*-
from application import app

# define some constants
REQUEST_BASE_URL = 'https://api.twitter.com'
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTH_TOKEN_URL = 'https://api.twitter.com/oauth/authenticate?oauth_token={}'
HTTP_METHOD = 'GET'
USER_TIMELINE_URL = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

INIT_ERROR = 'init_error'

try:
    CONSUMER_KEY = app.config['TW_CONSUMER_KEY']
    CONSUMER_SECRET = app.config['TW_CONSUMER_SECRET']
    TOKEN = app.config['TW_TOKEN']
    TOKEN_SECRET = app.config['TW_TOKEN_SECRET']
except:
    CONSUMER_KEY = INIT_ERROR
    CONSUMER_SECRET = INIT_ERROR
    TOKEN = INIT_ERROR
    TOKEN_SECRET = INIT_ERROR

# set logger
logger = logging.getLogger('modules.twoauth')


class OAuthBase(object):

    # write common code between oauth 1 and oauth 2 here
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret


class OAuth10(OAuthBase):
    """
    use this class for OAuth 1.0 and XAuth, diff being for XAuth, we use
    token_secret only to sign request and consumer key/secret are annonymouse
    """
    def __init__(self, consumer_key, consumer_secret):
        self.oauth_version = '1.0'
        super(OAuth10, self).__init__(consumer_key=consumer_key,
                                      consumer_secret=consumer_secret)

    def url_escape(self, text):
        """
        encodes text, as per OAUTH standards Characters in the unreserved
        character set (ALPHA, DIGIT, "-", ".", "_", "~")
        MUST NOT be encoded.
        @param text - text to be url encoded
        @return url quoted text
        """
        try:
            escaped_text = urllib.quote(text, safe='~')
        except Exception as e:
            escaped_text = None
            logger.error('oauth10.url_escape - %s' % e)

        return escaped_text

    def url_unescape(self, text):
        """
        return url unquoted text
        @param text - text to be unquoted
        @return unquoted text
        """
        return urllib.unquote(text)

    def convert_params_to_query_str(self, param_map):
        """
        converts parameters into a URL query string.

        @param param_map: a key-value map.
        @return a URL query string version of the given parameters.
        """
        params = []
        for param in sorted(param_map.iteritems(), key=lambda x: x[0]):
            params.append('%s=%s' % (param[0], self.url_escape(param[1])))
        return '&'.join(params)

    def get_request_base_string(self, elements):
        """
        escapaes the each element passed and joins with & to form base_string
        for signatures
        @param elements: a dict/list of elements to be joined using '&' with
            each other
        @return join of escaped elements
        """
        escape_str = '&'.join([self.url_escape(x) for x in elements])
        return escape_str

    def generate_encoded_signature(self, base_str, token_secret):
        """
        creates a composite signing key and uses the composite signing key to
        create an oauth_signature from the signature base string by signing
        the base string using the composite signing key. SHA1 method is used
        for signing
        @param base_str - string to be signed
        @param token_secret - oauth_token_secret
        @return signed base_str with composite key
        """
        hmac_key = '&'.join([self.url_escape(self.consumer_secret),
                             self.url_escape(token_secret)])
        digest = hmac.new(hmac_key, base_str, hashlib.sha1)
        encoded_signature = base64.b64encode(digest.digest())
        return encoded_signature

    def get_common_oauth_params(self):
        """
        gets parameters that are common to all oauth requests.
        """
        oauth_params = {}
        oauth_params['oauth_consumer_key'] = self.consumer_key
        oauth_params['oauth_nonce'] = str(random.randrange(2 ** 64 - 1))
        oauth_params['oauth_signature_method'] = 'HMAC-SHA1'
        oauth_params['oauth_version'] = self.oauth_version
        oauth_params['oauth_timestamp'] = str(int(time.time()))

        return oauth_params

    def generate_oauth_string(self, method=HTTP_METHOD, apiurl='',
                              oauth_params=None, remove_secret=True,
                              query_params={}):
        """
        Generates an OAUTH 1.0 authentication base string. This string will
        be signed later to form signed request
        @param method GET/POST
        @param apiurl request url
        @param oauth_params dict containing oauth params
        @param remove_secret indicating whether to remove oauth_token_secret
        from oauth_params. Generally for requests secret is used only for
        signing and not in generating oauth string
        @param query_params dict containing params to be passed as query
        string, used only for generating base string and signature, not used
        for final Oauth string
        """
        if not apiurl or apiurl.strip() == '':
            return

        pre_encoded_string = None

        if not oauth_params:
            oauth_params = self.get_common_oauth_params()

        try:
            oauth_token_secret = oauth_params['oauth_token_secret']
        except:
            oauth_token_secret = ''

        if remove_secret:
            try:
                del oauth_params['oauth_token_secret']
            except KeyError:
                pass
        try:
            oauth_params.update(query_params)
        except:
            pass

        try:
            request_url_base = apiurl
            # convert the parameter map into a URL query string
            url_query_str = self.convert_params_to_query_str(oauth_params)

            # join method, request_url and formatted string
            oauth_base_string = self.get_request_base_string([
                method, request_url_base, url_query_str])

            # generate auth signature
            encoded_signature = self.generate_encoded_signature(
                    oauth_base_string, oauth_token_secret)

            oauth_params['oauth_signature'] = encoded_signature

            # remove query params, required only for generating base string
            try:
                for k in query_params.keys():
                    del oauth_params[k]
            except:
                pass

            # join the parameters using comma
            comma_joined_params = []
            for k, v in sorted(oauth_params.iteritems()):
                comma_joined_params.append('%s="%s"' % (k, self.url_escape(v)))
            param_list = ','.join(comma_joined_params)

            pre_encoded_string = param_list

        except Exception as e:
            logger.error('oauth10.generate_oauth_string - exception ' +
                         'while generating oauth string {}'.format(e))
            pass

        return pre_encoded_string


class OAuth20(OAuthBase):
    """
    oauth 2.0 class
    """

    def __init__(self, consumer_key, consumer_secret):
        self.oauth_version = '2.0'
        super(OAuth20, self).__init__(consumer_key=consumer_key,
                                      consumer_secret=consumer_secret)


class TwitterOAuth10(OAuth10):

    def __init__(self):
        # host is required, we will genereate key/secret from method above
        super(TwitterOAuth10, self).__init__(consumer_key=CONSUMER_KEY,
                                             consumer_secret=CONSUMER_SECRET)

    def get_request_token(self, callback):
        method = 'POST'
        apiurl = REQUEST_TOKEN_URL
        # for local testing use oob as twitter treats localhost urls like a
        # desktop application
        # oauth_callback = 'oob'
        oauth_params = self.get_common_oauth_params()
        oauth_params['oauth_callback'] = callback

        oauth_header = self.get_header(method, apiurl, oauth_params)

        response = None
        content = None
        response, content = self.request_twitter(apiurl, method, oauth_header)

        if content and content.strip() != '':
            # separate the token and token secrets
            # response is something like oauth_token=2F1sSanf&
            # oauth_token_secret=9uZdktN&oauth_callback_confirmed=true
            try:
                request_token = dict(
                        info.split('=') for info in content.split('&'))
            except:
                return None

            # exchange this token for authorization
            api = AUTH_TOKEN_URL.format(str(request_token['oauth_token']))
            request_token['api'] = api
            return request_token

        return None

    def get_access_token(self, oauth_token, oauth_verifier,
                         oauth_token_secret, oauth_callback):
        """
        get access token for a user
        """
        method = 'POST'
        apiurl = ACCESS_TOKEN_URL

        # for local testing use oob as twitter treats localhost urls like a
        # desktop application
        # oauth_callback = 'oob'
        oauth_params = self.get_common_oauth_params()
        oauth_params['oauth_callback'] = oauth_callback
        oauth_params['oauth_token'] = oauth_token
        oauth_params['oauth_verifier'] = oauth_verifier
        oauth_params['oauth_token_secret'] = oauth_token_secret

        oauth_header = self.get_header(method, apiurl, oauth_params)
        response, content = self.request_twitter(apiurl, method, oauth_header)
        if content and content.strip() != '':
            # separate the token and token secrets
            try:
                access_token = dict(
                        info.split('=') for info in content.split('&'))
            except:
                return None

            return access_token

        return None

    def get_header(self, method=HTTP_METHOD, apiurl='',
                   oauth_params=None, query_params={}):

        oauth_string = self.generate_oauth_string(
                method=method, apiurl=apiurl, oauth_params=oauth_params,
                query_params=query_params)
        auth_header = 'OAuth %s' % oauth_string
        return {'Authorization': auth_header}

    def request_twitter(self, api='', method=HTTP_METHOD, oauth_header=None,
                        params=None):
        """
        Requests twitter with a url and fetches results.
        Doc - https://dev.twitter.com/docs/auth/oauth

        Arguments:
            api - url to be fetched
            method - type of request GET/PUT/POST/DELETE
            oauth_header - oauth Authorization header after signing properly
            params - request params to be passed to twitter as request body
        Returns:
            response - Request response inlcudes status, content length etc etc
            content - Request content e.g. tweets in XML format for tweets
                request
        """

        if not api or api.strip() == '':
            return None

        request_headers = None
        if oauth_header:
            request_headers = oauth_header

        qs = None
        if params and len(params) > 0 and isinstance(params, dict):
            qs = urllib.urlencode(params)

        if qs:
            api = api + '?' + qs

        result = urlfetch.fetch(api, method=method, headers=request_headers)
        content = result.content if result.status_code == 200 else None
        return (result.status_code, content)

    def get_user_timeline(self, oauth_token=TOKEN,
                          oauth_token_secret=TOKEN_SECRET, last_tweet=''):
        """
        gets user timeline to fetch tweets
        doc - https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline
        """
        method = 'GET'
        if oauth_token == INIT_ERROR or oauth_token_secret == INIT_ERROR:
            return

        oauth_params = self.get_common_oauth_params()
        oauth_params['oauth_token'] = oauth_token
        oauth_params['oauth_token_secret'] = oauth_token_secret

        apiurl = USER_TIMELINE_URL
        query_params = {
            'include_entities': 'true',
            'count': '100',
            'exclude_replies': 'false',
            'include_rts': 'true'
        }
        # if we have last tweet id, then use it else fetch latest 20 tweets
        # (can be increased later)
        if last_tweet and str(last_tweet).strip() != '':
            query_params['since_id'] = str(last_tweet).strip()

        oauth_header = self.get_header(method, apiurl, oauth_params,
                                       query_params=query_params)
        response, content = ['', '']
        response, content = self.request_twitter(apiurl, method, oauth_header,
                                                 query_params)
        return content
