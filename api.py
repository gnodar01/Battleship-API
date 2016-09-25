# -*- coding: utf-8 -*-`
"""
api.py - Udacity conference server-side Python App Engine API;
            uses Google Cloud Endpoints

    for Fullstack Nanodegree Project

    created by Nodari Gogoberidze - June 2016
"""

from math import log
import json
from re import match
# import logging
import endpoints
from google.appengine.ext import ndb
from protorpc import remote, messages, message_types
from google.appengine.api import memcache
# from google.appengine.api import taskqueue

from models.ndbModels import User, Game, Piece, Miss
from models.protorpcModels import StringMessage, GameStatusMessage, UserGames, Ranking, Rankings, GameHistory, MoveDetails
from models.requests import (UserRequest, NewGameRequest, USER_GAMES_REQUEST, JOIN_GAME_REQUEST,
                             PLACE_PIECE_REQUEST, STRIKE_REQUEST, GAME_REQUEST, PLACE_DUMMY_PIECES_REQUEST)
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


# TODO: Authentication for each of the methods
@endpoints.api(name='battle_ship', version='v1')
class BattleshipAPI(remote.Service):
    """Battle Ship API"""

# - - - - User Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _get_user(self, username):
        """Takes in the name of a player/user, and returns a user query object"""
        user = User.query(User.name == username).get()
        if not user:
            raise endpoints.ConflictException('{} does not exist.'.format(username))
        return user


    @endpoints.method(request_message=UserRequest,
                      response_message=StringMessage,
                      path='user/new',
                      name='user.create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        email_format_match = match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', request.email)
        if not email_format_match:
            raise endpoints.ConflictException('E-mail is not valid')
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException('A User with that name already exists')
        if User.query(User.email == request.email).get():
            raise endpoints.ConflictException('A User with that E-Mail already exists')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

# - - - - Game Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(request_message=NewGameRequest,
                      response_message=StringMessage,
                      path='game/new',
                      name='game.create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a new Game"""
        if request.player_one_name == request.player_two_name:
            raise endpoints.ConflictException('Player one cannot be the same as player two.')
        player_one = self._get_user(request.player_one_name)

        if request.player_two_name:
            player_two = self._get_user(request.player_two_name)
            game = Game(player_one=player_one.key, player_turn=player_one.key, player_two=player_two.key)
            game.put()
            return StringMessage(message=str(game.key.urlsafe()))
        else:
            game = Game(player_one=player_one.key, player_turn=player_one.key)
            game.put()
            return StringMessage(message=str(game.key.urlsafe()))

    @endpoints.method(request_message=JOIN_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/join/{url_safe_game_key}',
                      name='game.join_game',
                      http_method='POST')
    def join_game(self, request):
        """Join a game if not already full"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        if game.player_two:
            raise endpoints.ConflictException('This game is already full!')
        else:
            player_two = self._get_user(request.player_two_name)
            player_one = game.player_one.get()
            if player_two == player_one:
                raise endpoints.ConflictException('Player one and player two cannot be the same.')
            game.player_two = player_two.key
            game.put()
        return StringMessage(message=str(game))

# - - - - Place piece methods - - - - - - - - - - - - - - - - - - - - - - - - -

    def _coord_validity_check(self, row_coord, col_coord):
        """Raise errors if the row or column coordinates are not valid"""
        if row_coord not in ROWS:
            raise endpoints.ConflictException('Row coordinate must be between 1 - 10')
        if col_coord not in COLUMNS:
            raise endpoints.ConflictException('Column coordinate must be between A - J')

    def _board_boundaries_check(self, piece_alignment, num_spaces, row_index, col_index):
        """Raise errors if the peice is being placed outside of the bounds of the board"""
        if (piece_alignment == 'vertical' and row_index + num_spaces > len(ROWS)):
            raise endpoints.ConflictException('Your piece has gone past the boundaries of the board')
        if (piece_alignment == 'horizontal' and col_index + num_spaces > len(COLUMNS)):
            raise endpoints.ConflictException('Your piece has gone past the boundaries of the board')

    def _all_coords(self, piece_alignment, num_spaces, row_index, col_index):
        """Get all coordinates of the piece based on it's starting coordinates and piece size"""
        if piece_alignment == 'vertical':
            columns = COLUMNS[col_index]
            rows = ROWS[row_index : row_index + num_spaces]
        else:
            columns = COLUMNS[col_index : col_index + num_spaces]
            rows = ROWS[row_index]
        return [(col + row) for col in columns for row in rows]

    @endpoints.method(request_message=PLACE_PIECE_REQUEST,
                      response_message=StringMessage,
                      path='game/place_piece/{url_safe_game_key}',
                      name='game.place_piece',
                      http_method='POST')
    def place_piece(self, request):
        """Set up a player's board pieces"""
        # Raise errors if the row or column coordinates are not valid
        if request.first_row_coordinate not in ROWS:
            raise endpoints.ConflictException('Row coordinate must be between 1 - 10')
        if request.first_column_coordinate.upper() not in COLUMNS:
            raise endpoints.ConflictException('Column coordinate must be between A - J')
        # self._coord_validity_check(request.first_row_coordinate, request.first_column_coordinate.upper())

        num_spaces = PIECES[request.piece_type.name]['spaces']
        row_index = ROWS.index(request.first_row_coordinate)
        col_index = COLUMNS.index(request.first_column_coordinate.upper())

        # Raise errors if the peice is being placed outside of the bounds of the board
        if (request.piece_alignment.name == 'vertical' and row_index + num_spaces > len(ROWS)):
            raise endpoints.ConflictException('Your piece has gone past the boundaries of the board')
        if (request.piece_alignment.name == 'horizontal' and col_index + num_spaces > len(COLUMNS)):
            raise endpoints.ConflictException('Your piece has gone past the boundaries of the board')
        # self._board_boundaries_check(request.piece_alignment.name, num_spaces, row_index, col_index)

        game = get_by_urlsafe(request.url_safe_game_key, Game)
        player = User.query(User.name == request.player_name).get()

        # Raise error if all of the pieces for this player and this game have been placed already
        if game.game_started:
            raise endpoints.ConflictException('All of the pieces for this game have already been placed')

        # Get all coordinates of the piece based on it's starting coordinates and piece size
        if request.piece_alignment.name == 'vertical':
            columns = COLUMNS[col_index]
            rows = ROWS[row_index : row_index + num_spaces]
        else:
            columns = COLUMNS[col_index : col_index + num_spaces]
            rows = ROWS[row_index]
        coordinates = [(col + row) for col in columns for row in rows]
        # coordinates = self._all_coords(request.piece_alignment.name, num_spaces, row_index, col_index)

        # Errors based on player's previously placed pieces for this game
        player_pieces = Piece.query().filter(Piece.game == game.key, Piece.player == player.key).fetch()
        for placed_piece in player_pieces:
            # Raise error if the piece has already been placed on the player's board
            if placed_piece.ship == request.piece_type.name:
                raise endpoints.ConflictException('This piece has already been placed for this player')
            # Raise error if piece intersects with any other piece
            for placed_coordinate in placed_piece.coordinates:
                if placed_coordinate in coordinates:
                    raise endpoints.ConflictException('Your piece intersects with {}'.format(placed_coordinate))

        piece = Piece(game=game.key, player=player.key, ship=request.piece_type.name, coordinates=coordinates)
        player_pieces.append(piece)
        piece.put()

        # Check if all pieces for this player & game have been placed
        if len(player_pieces) == len(PIECES):
            if player.key == game.player_one:
                game.player_one_pieces_loaded = True
            else:
                game.player_two_pieces_loaded = True
            # Start game if all pieces for both players have been loaded
            if game.player_one_pieces_loaded == True and game.player_two_pieces_loaded == True:
                game.game_started = True
            game.put()

        return StringMessage(message=str([piece.ship for piece in player_pieces]))

# - - - - Strike Coord Methods  - - - - - - - - - - - - - - - - - - - - - - - -

    def _change_player_turn(self, game):
        if game.player_turn == game.player_one:
            game.player_turn = game.player_two
        else:
            game.player_turn = game.player_one
        game.put()

    def _game_over_status(self, game, target_player):
        target_player_pieces = Piece.query(Piece.game == game.key).filter(Piece.player == target_player.key).fetch()
        for piece in target_player_pieces:
            if piece.sunk == False:
                return game.game_over
        game.game_over = True
        game.put()
        return game.game_over

    def _piece_sunk_status(self, piece):
        if sorted(piece.coordinates) == sorted(piece.hit_marks):
            piece.sunk = True
            piece.put()
        return piece.sunk

    def _log_history(self, game, target_player, attacking_player, coord, status, piece_name=None):
        move_details = {'target_player': target_player.name,
                        'attacking_player': attacking_player.name,
                        'target_coordinate': coord,
                        'status': status}
        if piece_name:
            move_details['ship_type'] = piece_name
        game.history.append(move_details)
        game.put()


    @endpoints.method(request_message=STRIKE_REQUEST,
                      response_message=StringMessage,
                      path='game/strike/{url_safe_game_key}',
                      name='game.strike_coordinate',
                      http_method='POST')
    def strike_coord(self, request):
        """Make a move to strike a given coordinate"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)

        if game.game_over == True:
            raise endpoints.ConflictException('This game has already ended')

        if game.game_started == False:
            raise endpoints.ConflictException('This game has not started yet, all the pieces must first be loaded by both players')

        target_coord = request.coordinate.upper()

        # Player who's board is being attacked
        # TODO: Raise error if player not registered for this game
        attacking_player = game.player_turn.get()
        target_player = self._get_user(request.target_player)

        if attacking_player == target_player:
            raise endpoints.ConflictException('It is not this player\'s turn')

        # TODO: check if request.coordinate is a valid coordinate
        
        target_player_pieces = Piece.query(Piece.game == game.key).filter(Piece.player == target_player.key).fetch()
        target_player_pieces_hit_coords = [piece.hit_marks for piece in target_player_pieces]

        # Coordinates that have been previously hit against target player
        for piece_hit_coords in target_player_pieces_hit_coords:
            if target_coord in piece_hit_coords:
                raise endpoints.ConflictException('This coordinate has already been hit')

        # Coordinates that have been previously attempted and missed against target player
        misses = Miss.query(Miss.game == game.key).filter(Miss.target_player == target_player.key).fetch()
        miss_coords = [missCoord.coordinate for missCoord in misses]

        if target_coord in miss_coords:
            raise endpoints.ConflictException('This coordinate has already been struck and missed')

        # Change it to the other player's turn
        if game.player_turn == game.player_one:
            game.player_turn = game.player_two
        else:
            game.player_turn = game.player_one
        game.put()
        # self._change_player_turn(game)

        for piece in target_player_pieces:
            # If a ship is hit
            if target_coord in piece.coordinates:
                piece.hit_marks.append(target_coord)
                piece.put()
                # check if piece sunk
                piece_sunk = self._piece_sunk_status(piece)
                # check if game_over
                game_over = self._game_over_status(game, target_player)
                if game_over:
                    game.winner = attacking_player.key
                    game.put()
                    # Log history of hit
                    self._log_history(game, target_player, attacking_player, target_coord, 'Hit - Sunk Ship: Game Over', piece_name=piece.ship)
                    return StringMessage(message="{} sunk, game over!".format(piece.ship))
                elif piece_sunk:
                    self._log_history(game, target_player, attacking_player, target_coord, 'Hit - Sunk Ship', piece_name=piece.ship)
                    return StringMessage(message="{} sunk!".format(piece.ship))
                else:
                    self._log_history(game, target_player, attacking_player, target_coord, 'Hit', piece_name=piece.ship)
                    return StringMessage(message="Hit {}!".format(piece.ship))

        # If no ship is hit
        self._log_history(game, target_player, attacking_player, target_coord, 'Miss')
        Miss(game=game.key, target_player=target_player.key, coordinate=target_coord).put()
        return StringMessage(message="miss")

# - - - - Info Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _copy_game_to_form(self, game_obj):
        game_form = GameStatusMessage()
        setattr(game_form, "game_key", str( game_obj.key.urlsafe() ))
        for field in game_form.all_fields():
            if field.name == "player_one" or field.name == "player_two" or field.name == "player_turn" or field.name == "winner":
                player_key = getattr(game_obj, field.name)
                if player_key:
                    player = player_key.get()
                    setattr(game_form, field.name, player.name)
                else:
                    setattr(game_form, field.name, "None")
            elif hasattr(game_obj, field.name):
                setattr(game_form, field.name, str(getattr(game_obj, field.name)))
        return game_form

    def _copy_ranking_to_form(self, index, user_scores):
        ranking_form = Ranking()
        setattr(ranking_form, "username", user_scores[0])
        setattr(ranking_form, "ranking", index+1)
        setattr(ranking_form, "games_won", user_scores[1])
        setattr(ranking_form, "games_lost", user_scores[2])
        setattr(ranking_form, "score", user_scores[3])
        return ranking_form

    def _copy_move_details_to_form(self, index, game):
        move_details_form = MoveDetails()
        setattr(move_details_form, "target_player_name", game['target_player'])
        setattr(move_details_form, "attacking_player_name", game['attacking_player'])
        setattr(move_details_form, "target_coordinate", game['target_coordinate'])
        setattr(move_details_form, "status", game['status'])
        setattr(move_details_form, "move_number", index+1)
        if 'ship_type' in game:
            setattr(move_details_form, "ship_type", game['ship_type'])
        return move_details_form

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/coords/{url_safe_game_key}',
                      name='game.get_coords',
                      http_method='GET')
    def get_coords(self, request):
        """Get currently populated coordinates in a game by player"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        p_one_pieces = Piece.query().filter(Piece.game == game.key, Piece.player == game.player_one).fetch()
        p_one_coords = [(piece.ship, piece.coordinates) for piece in p_one_pieces]
        p_two_pieces = Piece.query().filter(Piece.game == game.key, Piece.player == game.player_two).fetch()
        p_two_coords = [(piece.ship, piece.coordinates) for piece in p_two_pieces]
        return StringMessage(message="Player one coordinates: {}; Player two coordinates: {}".format(str(p_one_coords), str(p_two_coords)))

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=GameStatusMessage,
                      path='game/status/{url_safe_game_key}',
                      name='game.get_game_status',
                      http_method='GET')
    def get_game_status(self, request):
        """Get a game's current status"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        # TODO: if game exists
        return self._copy_game_to_form(game)

# - - - - Extended Methods  - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _win_loss_list(self, games):
        """Returns a dict of wins and losses for each user by querying a list of all games with status game_over == True"""
        win_loss = {}
        for game in games:
            game_winner = game.winner
            if game_winner == game.player_one:
                game_loser = game.player_two
            else:
                game_loser = game.player_one
            game_winner = game_winner.get().name
            game_loser = game_loser.get().name

            if game_winner in win_loss:
                win_loss[game_winner]['won'] += 1
            else:
                win_loss[game_winner] = {'won': 1, 'lost': 0}
            if game_loser in win_loss:
                win_loss[game_loser]['lost'] += 1
            else:
                win_loss[game_loser] = {'won': 0, 'lost': 1}
        return win_loss

    def _assign_rankings(self, win_loss, total_games):
        """Takes in a dict of wins & losses by user, returns list of rankings
        based on the reatio of their wins compared to losses, and the total
        number of games played by all users, plus a reward factor based on the
        number of games played by the user with respect to total number of
        games played overall"""
        rankings = win_loss
        for user in win_loss:
            won = win_loss[user]['won']
            lost = win_loss[user]['lost']
            win_diff = float(won - lost)
            games_played = float(won + lost)
            score = (win_diff / total_games) + log(games_played, total_games)
            rankings[user]['score'] = score
        return rankings

    def _sort_rankings(self, rankings):
        """Takes in in a dict of rankings, return list of tuples with username, wins, losses, score; sorted by score"""
        ranking_list = []
        for user in rankings:
            wins = rankings[user]['won']
            losses = rankings[user]['lost']
            score = rankings[user]['score']
            ranking_list.append((user, wins, losses, score))
        # Good ol' martian smiley: http://stackoverflow.com/questions/3705670/best-way-to-create-a-reversed-list-in-python
        return sorted(ranking_list, key=lambda tup: tup[3])[::-1]

    @endpoints.method(request_message=USER_GAMES_REQUEST,
                      response_message=UserGames,
                      path='user/games/{user_name}',
                      name='game.get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of a User's active games"""
        # it might make sense for each game to be a descendant of a User
        user = User.query(User.name == request.user_name).get()
        user_games = Game.query(ndb.OR(Game.player_one == user.key,
                                            Game.player_two == user.key))

        if request.include != None and request.include.lower() in ['wins', 'losses']:
            if request.include.lower() == 'wins':
                user_games = user_games.filter(Game.winner == user.key).fetch()
            elif request.include.lower() == 'losses':
                user_games = user_games.filter(Game.winner != user.key).filter(Game.winner != None).fetch()
        else:
            user_games = user_games.fetch()
        # TODO: if any games
        return UserGames(games=[self._copy_game_to_form(game) for game in user_games])

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{url_safe_game_key}',
                      name='game.cancel_game',
                      http_method='GET')
    def cancel_game(self, request):
        """Cancels an active game"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        if game:
            game_pieces = Piece.query(Piece.game == game.key).fetch()
            game_misses = Miss.query(Miss.game == game.key).fetch()
            for piece in game_pieces:
                piece.key.delete()
            for miss in game_misses:
                miss.key.delete()
            game.key.delete()
            return StringMessage(message="Game deleted")
        else:
            return StringMessage(message="Game does not exist")

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=Rankings,
                      path='rankings',
                      name='get_rankings',
                      http_method='GET')
    def get_user_ranks(self, request):
        """Gets list of user rankings"""
        completed_games = Game.query().filter(Game.game_over == True).fetch()
        total_games = len(completed_games)
        win_loss = self._win_loss_list(completed_games)
        rankings = self._assign_rankings(win_loss, total_games)
        sorted_rankings = self._sort_rankings(rankings)
        return Rankings(rankings=[self._copy_ranking_to_form(index, score) for index, score in enumerate(sorted_rankings)])

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=GameHistory,
                      path='game/history/{url_safe_game_key}',
                      name='game.get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Gets history of all moves played for a given game"""
        game_history = get_by_urlsafe(request.url_safe_game_key, Game).history
        return GameHistory(moves=[self._copy_move_details_to_form(index, game) for index, game in enumerate(game_history)])

# - - - temp api to place dummy pices in the datastore  - - - - - - - - - - - -

    @endpoints.method(request_message=PLACE_DUMMY_PIECES_REQUEST,
                      response_message=StringMessage,
                      path='game/place_pieces/{url_safe_game_key}',
                      name='game.place_dummy_pieces',
                      http_method='POST')
    def place_dummy_pieces(self, request):
        """Place dummy pieces"""
        # TODO: Check if game exists
        # TODO: If player one or player two does not exist, raise error
        # TODO: Check that game has no pieces laid
        players = (User.query(User.name == request.player_one).get(), User.query(User.name == request.player_two).get())
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        pieces = [piece for piece in PIECES]
        coord_set = [['A1','A2','A3','A4','A5'],['B1','B2','B3','B4'],['C1', 'C2', 'C3'],['D1','D2','D3'],['E1','E2']]
        for i in range(0,len(PIECES)):
            for player in players:
                Piece(game=game.key, player=player.key, ship=pieces[i], coordinates=coord_set[i]).put()
        game.game_started = True
        game.player_one_pieces_loaded = True
        game.player_two_pieces_loaded = True
        game.put()
        return StringMessage(message=str(game.key.urlsafe()))

    @endpoints.method(request_message=PLACE_DUMMY_PIECES_REQUEST,
                      response_message=StringMessage,
                      path='game/place_pieces/mostly_hit/{url_safe_game_key}',
                      name='game.place_dummy_mostly_hit_pieces',
                      http_method='POST')
    def place_dummy_mostly_hit_pieces(self, request):
        """Place dummy pieces"""
        # TODO: Check if game exists
        # TODO: If player one or player two does not exist, raise error
        # TODO: Check that game has no pieces laid
        players = (User.query(User.name == request.player_one).get(), User.query(User.name == request.player_two).get())
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        pieces = [piece for piece in PIECES]
        coord_set = [['A1','A2','A3','A4','A5'],['B1','B2','B3','B4'],['C1', 'C2', 'C3'],['D1','D2','D3'],['E1','E2']]
        hits = [['A1','A2','A3','A4','A5'],['B1','B2','B3','B4'],['C1', 'C2', 'C3'],['D1','D2','D3'],['E1']]
        sunk_status = [True,True,True,True,False]
        for i in range(0,len(PIECES)):
            for player in players:
                Piece(game=game.key, player=player.key, ship=pieces[i], coordinates=coord_set[i], hit_marks=hits[i], sunk=sunk_status[i]).put()
        game.game_started = True
        game.player_one_pieces_loaded = True
        game.player_two_pieces_loaded = True
        game.put()
        return StringMessage(message=str(game.key.urlsafe()))

    @staticmethod
    def _cache_average_moves():
        """Populates memcache with the average number of moves per Game"""
        games = Game.query(Game.game_over == True).fetch()
        num_games = len(games)
        sum_history = 0
        for game in games:
            if game.game_history:
                sum_history += len(game.game_history)
        average = float(sum_history) / num_games
        memcache.set(key='MOVES_PER_GAME',
                     value='The average moves per game is {:.2f}'.format(average))



api = endpoints.api_server([BattleshipAPI])
