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

from models.nbdModels import User, Game
from models.protorpcModels import StringMessage
from models.requests import UserRequest, NewGameRequest, JoinGameRequest, PlacePieceRequest
from utils import get_by_urlsafe

PIECES = {
    'aircraft_carrier': {'name': 'Aircraft Carrier', 'spaces': 5},
    'battleship': {'name': 'Battleship', 'spaces': 4},
    'submarine': {'name': 'Submarine', 'spaces': 3},
    'destroyer': {'name': 'Destroyer', 'spaces': 3},
    'patrol_ship': {'name': 'Patrol Ship', 'spaces': 2}
}

COLUMNS = ['a','b','c','d','e','f','g','h','i','j']


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
                      path='game/new',
                      name='create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a new Game"""
        # TODO: if playerOne does not exist return error
        playerOne = User.query(User.name == request.player_one_name).get()
        if request.player_two_name:
            # TODO: if playerTwo does not exist throw error
            playerTwo = User.query(User.name == request.player_two_name).get()
            game = Game(player_one=playerOne.key, player_two=playerTwo.key)
            print game
            # game.put()
            return StringMessage(message='player one is {}, player two is {}'.format(playerOne.name, playerTwo.name))
        else:
            game = Game(player_one=playerOne.key)
            print game
            # game.put()
            return StringMessage(message='player one is {}'.format(playerOne.name))

    @endpoints.method(request_message=JoinGameRequest,
                      response_message=StringMessage,
                      path='game/join',
                      name='join_game',
                      http_method='POST')
    def join_game(self, request):
        """Join a game if not already full"""
        game = get_by_urlsafe(request.game_key, Game)
        if game.player_two:
            raise endpoints.ConflictException(
                    'This game is already full!')
        else:
            # TODO: if playerTwo does not exist raise error
            playerTwo = User.query(User.name == request.player_two_name).get()
            game.player_two = playerTwo.key
            # game.put()
        return StringMessage(message=str(game))

    @endpoints.method(request_message=PlacePieceRequest,
                      response_message=StringMessage,
                      path='game/setup/place_piece',
                      name='place_piece',
                      http_method='POST')
    def place_piece(self, request):
        """Set up a player's board pieces"""
        if request.first_row_coordinate not in range(1,11):
            raise endpoints.ConflictException('Row coordinate must be between 1 - 10')
        if (request.piece_alignment.name == 'vertical' and
            request.first_row_coordinate + PIECES[request.piece_type.name]['spaces'] > 10):
            raise endpoints.ConflictException('Your piece has gone past the boundaries of the board')
        if (request.piece_alignment.name == 'horizontal' and
            COLUMNS.index(request.first_column_coordinate.name) + PIECES[request.piece_type.name]['spaces'] > len(COLUMNS)):
            raise endpoints.ConflictException('Your piece has gone past the boundaries of the board')


        # game = get_by_urlsafe(request.game_key, Game)
        # player = User.query(User.name == request.player_name).get()
        
        return StringMessage(message=str(request.first_row_coordinate))









api = endpoints.api_server([BattleshipAPI])
