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

from models.nbdModels import User, Game, Piece
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

COLUMNS = ['A','B','C','D','E','F','G','H','I','J']
ROWS = ['1','2','3','4','5','6','7','8','9','10']
GRID = [(column, row) for column in COLUMNS for row in ROWS]


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
            game.put()
            return StringMessage(message='player one is {}, player two is {}'.format(playerOne.name, playerTwo.name))
        else:
            game = Game(player_one=playerOne.key)
            print game
            game.put()
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
            game.put()
        return StringMessage(message=str(game))

    @endpoints.method(request_message=PlacePieceRequest,
                      response_message=StringMessage,
                      path='game/setup/place_piece',
                      name='place_piece',
                      http_method='POST')
    def place_piece(self, request):
        """Set up a player's board pieces"""
        # Raise errors if the row or column coordinates are not valid
        if request.first_row_coordinate not in ROWS:
            raise endpoints.ConflictException('Row coordinate must be between 1 - 10')
        if request.first_column_coordinate.upper() not in COLUMNS:
            raise endpoints.ConflictException('Column coordinate must be between A - J')

        numSpaces = PIECES[request.piece_type.name]['spaces']
        rowIndex = ROWS.index(request.first_row_coordinate)
        colIndex = COLUMNS.index(request.first_column_coordinate.upper())

        # Raise errors if the peice is being placed outside of the bounds of the board
        if (request.piece_alignment.name == 'vertical' and rowIndex + numSpaces > len(ROWS)):
            raise endpoints.ConflictException('Your piece has gone past the boundaries of the board')
        if (request.piece_alignment.name == 'horizontal' and colIndex + numSpaces > len(COLUMNS)):
            raise endpoints.ConflictException('Your piece has gone past the boundaries of the board')

        game = get_by_urlsafe(request.game_key, Game)
        player = User.query(User.name == request.player_name).get()

        # Raise error if all of the pieces for this player and this game have been placed already
        if game.pieces_loaded:
            raise endpoints.ConflictException('All of the pieces for this game have already been placed')

        # Get all coordinates of the piece based on it's starting coordinates and piece size
        if request.piece_alignment.name == 'vertical':
            columns = COLUMNS[colIndex]
            rows = ROWS[rowIndex:rowIndex + numSpaces]
        else:
            columns = COLUMNS[colIndex:colIndex + numSpaces]
            rows = ROWS[rowIndex]
        coordinates = [(col + row) for col in columns for row in rows]

        # Errors based on player's previously placed pieces for this game
        gamePlayerPieces = Piece.query().filter(Piece.game == game.key, Piece.player == player.key).fetch()
        for placedPiece in gamePlayerPieces:
            # Raise error if the piece has already been placed on the player's board
            if placedPiece.ship == request.piece_type.name:
                raise endpoints.ConflictException('This piece has already been placed for this player')
            # Raise error if piece intersects with any other piece
            for placedCoordinate in placedPiece.coordinates:
                if placedCoordinate in coordinates:
                    raise endpoints.ConflictException('Your piece intersects with {}'.format(placedCoordinate))

        piece = Piece(game=game.key, player=player.key, ship=request.piece_type.name, coordinates=coordinates)
        piece.put()

        # TODO: check if all pieces for this player & game have been placed

        return StringMessage(message=str(piece))









api = endpoints.api_server([BattleshipAPI])
