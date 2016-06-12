# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import 
from utils import get_by_urlsafe




@endpoints.api(name='battle-ship', version='v1')
class BattleshipAPI(remote.Service):
    """Game API"""
    @endpoints.method(request_message="",
                      response_message="",
                      path='',
                      name='',
                      http_method='POST')
    def create_user(self, request):
    	pass











api = endpoints.api_server([BattleshipAPI])