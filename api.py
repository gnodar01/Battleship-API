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
from models.requests import UserRequest, NewGameRequest
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
        # TODO: make sure user_name is min of 3 char and email is proper format (regex?)
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NewGameRequest,
                      response_message=StringMessage,
                      path='game',
                      name='create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a new Game"""
        pOne = User.query(User.name == request.player_one_name).get()
        pTwo = User.query(User.name == request.player_two_name).get()
        return StringMessage(message='player one is {}, player two is {}'.format(pOne.name, pTwo.name))











api = endpoints.api_server([BattleshipAPI])
