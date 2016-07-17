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

from models.nbdModels import User, Game, Piece, Miss
from models.protorpcModels import StringMessage
from models.requests import (UserRequest, NewGameRequest, JoinGameRequest, PlacePieceRequest,
                            CoordRequest, StrikeRequest, PlaceDummyPiecesRequest)
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
                      path='user/new',
                      name='user.create_user',
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
                      name='game.create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a new Game"""
        # TODO: if playerOne does not exist return error
        playerOne = User.query(User.name == request.player_one_name).get()
        if request.player_two_name:
            # TODO: if playerTwo does not exist throw error
            playerTwo = User.query(User.name == request.player_two_name).get()
            game = Game(player_one=playerOne.key, player_turn=playerOne.key, player_two=playerTwo.key)
            print game
            game.put()
            return StringMessage(message='player one is {}, player two is {}'.format(playerOne.name, playerTwo.name))
        else:
            game = Game(player_one=playerOne.key, player_turn=playerOne.key)
            print game
            game.put()
            return StringMessage(message='player one is {}'.format(playerOne.name))

    @endpoints.method(request_message=JoinGameRequest,
                      response_message=StringMessage,
                      path='game/join',
                      name='game.join_game',
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
                      path='game/place_piece',
                      name='game.place_piece',
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
        if game.game_started:
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
        placedShips = []
        for placedPiece in gamePlayerPieces:
            # Raise error if the piece has already been placed on the player's board
            if placedPiece.ship == request.piece_type.name:
                raise endpoints.ConflictException('This piece has already been placed for this player')
            # Raise error if piece intersects with any other piece
            for placedCoordinate in placedPiece.coordinates:
                if placedCoordinate in coordinates:
                    raise endpoints.ConflictException('Your piece intersects with {}'.format(placedCoordinate))
            placedShips.append(placedPiece.ship)

        piece = Piece(game=game.key, player=player.key, ship=request.piece_type.name, coordinates=coordinates)
        placedShips.append(piece.ship)
        piece.put()

        # Check if all pieces for this player & game have been placed
        if len(placedShips) == len(PIECES):
            if player.key == game.player_one:
                game.player_one_pieces_loaded = True
            else:
                game.player_two_pieces_loaded = True
            # Start game if all pieces for both players have been loaded
            if game.player_one_pieces_loaded == True and game.player_two_pieces_loaded == True:
                game.game_started = True
            game.put()

        return StringMessage(message=str(placedShips))

    @endpoints.method(request_message=StrikeRequest,
                      response_message=StringMessage,
                      path='game/strike',
                      name='game.strike_coordinate',
                      http_method='POST')
    def strike_coord(self, request):
        """Make a move to strike a given coordinate"""
        game = get_by_urlsafe(request.game_key, Game)
        if game.game_over == True:
            raise endpoints.ConflictException('This game has already ended')
        if game.game_started == False:
            raise endpoints.ConflictException('This game has not started yet')

        targetPlayer = User.query(User.name == request.target_player).get()

        if game.player_turn == targetPlayer.key:
            raise endpoints.ConflictException('It is not this player\'s turn')

        targetPlayerPieces = Piece.query().filter(Piece.game == game.key, Piece.player == targetPlayer.key).fetch()
        targetPlayerHitCoords = [piece.hit_marks for piece in targetPlayerPieces]

        for hitCoords in targetPlayerHitCoords:
            if request.coordinate.upper() in hitCoords:
                raise endpoints.ConflictException('This coordinate has already been hit')

        misses = Miss.query().filter(Miss.game == game.key, Miss.target_player == targetPlayer.key).fetch()
        missCoordinates = [missCoord.coordinate for missCoord in misses]

        if request.coordinate.upper() in missCoordinates:
            raise endpoints.ConflictException('This coordinate has already been struck and missed')

        print game.player_turn
        if game.player_turn == game.player_one:
            game.player_turn = game.player_two
        else:
            game.player_turn = game.player_one
        game.put()

        for piece in targetPlayerPieces:
            if request.coordinate.upper() in piece.coordinates:
                piece.hit_marks.append(request.coordinate.upper())
                piece.put()
                # TODO: check if piece sunk
                # TODO: check if game_over
                return StringMessage(message="hit")

        Miss(game=game.key, target_player=targetPlayer.key, coordinate=request.coordinate.upper()).put()
        return StringMessage(message="miss")


    @endpoints.method(request_message=CoordRequest,
                      response_message=StringMessage,
                      path='game/coords/{url_safe_game_key}',
                      name='game.get_coords',
                      http_method='GET')
    def get_coords(self, request):
        """Get currently populated coordinates in a game by player"""
        # WARNING  2016-07-10 03:25:55,285 api_config.py:1785] Method battle_ship.get_coords specifies path parameters but you are not using a
        # ResourceContainer. This will fail in future releases; please switch to using ResourceContainer as soon as possible.
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        pOnePieces = Piece.query().filter(Piece.game == game.key, Piece.player == game.player_one).fetch()
        pOneCoords = [(piece.ship, piece.coordinates) for piece in pOnePieces]
        pTwoPieces = Piece.query().filter(Piece.game == game.key, Piece.player == game.player_two).fetch()
        pTwoCoords = [(piece.ship, piece.coordinates) for piece in pTwoPieces]
        return StringMessage(message="Player one coordinates: {}; Player two coordinates: {}".format(str(pOneCoords), str(pTwoCoords)))

# - - - temp api to place dummy pices in the datastore - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(request_message=PlaceDummyPiecesRequest,
                      response_message=StringMessage,
                      path='game/placePieces',
                      name='game.place_dummy_pieces',
                      http_method='GET')
    def place_dummy_pieces(self, request):
        """Place dummy pieces"""
        players = (User.query(User.name == request.player_one).get(), User.query(User.name == request.player_two).get())
        game = get_by_urlsafe(request.game, Game)
        pieces = [piece for piece in PIECES]
        coordSet = [['A1','A2','A3','A4','A5'],['B1','B2','B3','B4'],['C1', 'C2', 'C3'],['D1','D2','D3'],['E1','E2']]
        for i in range(0,len(PIECES)):
            for player in players:
                Piece(game=game.key, player=player.key, ship=pieces[i], coordinates=coordSet[i]).put()
        game.game_started = True
        game.player_one_pieces_loaded = True
        game.player_two_pieces_loaded = True
        game.put()
        return StringMessage(message="donezo")





api = endpoints.api_server([BattleshipAPI])
