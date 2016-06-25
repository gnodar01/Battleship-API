# -*- coding: utf-8 -*-`
"""
api.py - Udacity conference server-side Python App Engine API;
            uses Google Cloud Endpoints

    for Fullstack Nanodegree Project

    created by Nodari Gogoberidze - June 2016
"""



# import logging
import endpoints
from protorpc import remote, messages, message_types
# from google.appengine.api import memcache
# from google.appengine.api import taskqueue

from models.nbdModels import User
from models.protorpcModels import StringMessage
from models.requests import UserRequest
# from utils import get_by_urlsafe



@endpoints.api(name='battle_ship', version='v1')
class BattleshipAPI(remote.Service):
    """Battle Ship API"""

    @endpoints.method(request_message=UserRequest,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=StringMessage,
                      path='game',
                      name='create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a new Game"""
        return StringMessage(message='')











api = endpoints.api_server([BattleshipAPI])
