# -*- coding: utf-8 -*-`
"""
api.py - Udacity conference server-side Python App Engine API;
            uses Google Cloud Endpoints

    for Fullstack Nanodegree Project

    created by Nodari Gogoberidze - June 2016
"""

from math import log
from re import match

import endpoints
from google.appengine.ext import ndb
from protorpc import remote, message_types
from google.appengine.api import memcache

from models.ndbModels import User, Game, Piece, Miss
from models.responses import (
    StringMessage,
    UserForm,
    GameStatusMessage,
    UserGames,
    PieceDetails,
    Coordinate,
    Ranking,
    Rankings,
    GameHistory,
    MoveDetails
)
from models.requests import (
    UserRequest,
    NewGameRequest,
    USER_GAMES_REQUEST,
    JOIN_GAME_REQUEST,
    PLACE_PIECE_REQUEST,
    STRIKE_REQUEST,
    GAME_REQUEST
)

from utils import get_by_urlsafe


PIECES = {
    'aircraft_carrier': {'name': 'Aircraft Carrier', 'spaces': 5},
    'battleship': {'name': 'Battleship', 'spaces': 4},
    'submarine': {'name': 'Submarine', 'spaces': 3},
    'destroyer': {'name': 'Destroyer', 'spaces': 3},
    'patrol_ship': {'name': 'Patrol Ship', 'spaces': 2}
}

COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
ROWS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
GRID = [(column + row) for column in COLUMNS for row in ROWS]


# TODO: Authentication for each of the methods
@endpoints.api(name='battle_ship', version='v1')
class BattleshipAPI(remote.Service):
    """Battle Ship API"""

# - - - - User Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _copy_user_to_form(self, user_obj):
        user_form = UserForm()
        setattr(user_form, 'name', getattr(user_obj, 'name'))
        setattr(user_form, 'email', getattr(user_obj, 'email'))
        return user_form

    def _get_user(self, username):
        """Takes in the name of a player/user,
        and returns a user query object"""
        user = User.query(User.name == username).get()
        if not user:
            raise endpoints.ConflictException(
                '{} does not exist.'.format(username))
        return user

    @endpoints.method(request_message=UserRequest,
                      response_message=UserForm,
                      path='user/new',
                      name='user.create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        email_format_match = match(
            r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
            request.email)

        if not email_format_match:
            raise endpoints.ConflictException('E-mail is not valid')

        if len(request.user_name) < 3:
            raise endpoints.ConflictException(
                'Username must be at least 3 characters')

        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists')

        if User.query(User.email == request.email).get():
            raise endpoints.ConflictException(
                'A User with that E-Mail already exists')

        user = User(name=request.user_name, email=request.email)
        user.put()
        return self._copy_user_to_form(user)

# - - - - Game Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _copy_game_to_form(self, game_obj):
        game_form = GameStatusMessage()

        setattr(game_form, "game_key", str(game_obj.key.urlsafe()))

        for field in game_form.all_fields():
            if (field.name == "player_one" or field.name == "player_two" or
                    field.name == "player_turn" or field.name == "winner"):

                player_key = getattr(game_obj, field.name)

                if player_key:
                    player = player_key.get()
                    setattr(game_form, field.name, player.name)
                else:
                    setattr(game_form, field.name, "None")

            elif hasattr(game_obj, field.name):
                setattr(game_form, field.name,
                        str(getattr(game_obj, field.name)))

        return game_form

    def _get_registered_player(self, game, username):
        player = self._get_user(username)
        if game.player_one != player.key and game.player_two != player.key:
            raise endpoints.ConflictException(
                '{} is not registered for this game'.format(player.name))
        return player

    @endpoints.method(request_message=NewGameRequest,
                      response_message=GameStatusMessage,
                      path='game/new',
                      name='game.create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a new Game"""
        if request.player_one_name == request.player_two_name:
            raise endpoints.ConflictException(
                'Player one cannot be the same as player two.')

        player_one = self._get_user(request.player_one_name)

        if request.player_two_name:
            player_two = self._get_user(request.player_two_name)
            game = Game(player_one=player_one.key,
                        player_turn=player_one.key,
                        player_two=player_two.key)
        else:
            game = Game(player_one=player_one.key, player_turn=player_one.key)
        game.put()
        return self._copy_game_to_form(game)

    @endpoints.method(request_message=JOIN_GAME_REQUEST,
                      response_message=GameStatusMessage,
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
                raise endpoints.ConflictException(
                    'Player one and player two cannot be the same.')

            game.player_two = player_two.key
            game.put()
        return self._copy_game_to_form(game)

# - - - - Place piece methods - - - - - - - - - - - - - - - - - - - - - - - - -

    def _piece_details_to_form(self, game, user, piece):
        piece_form = PieceDetails()
        setattr(piece_form, 'game_key', game.key.urlsafe())
        setattr(piece_form, 'owner', user.name)
        setattr(piece_form, 'ship_type', piece.ship)
        setattr(piece_form, 'coordinates',
                [Coordinate(coordinate=coord) for coord in piece.coordinates])
        return piece_form

    def _coords_validity_check(self, row_coord, col_coord):
        """Raise errors if the row or column coordinates are not valid"""
        if row_coord not in ROWS:
            raise endpoints.ConflictException(
                'Row coordinate must be between 1 - 10')

        if col_coord not in COLUMNS:
            raise endpoints.ConflictException(
                'Column coordinate must be between A - J')

    def _board_boundaries_check(self,
                                piece_alignment,
                                num_spaces,
                                row_index,
                                col_index):
        """Raise errors if the peice is being placed outside of the bounds of
        the board"""
        if (piece_alignment == 'vertical' and
                row_index + num_spaces > len(ROWS)):

            raise endpoints.ConflictException(
                'Your piece has gone past the boundaries of the board')

        if (piece_alignment == 'horizontal' and
                col_index + num_spaces > len(COLUMNS)):

            raise endpoints.ConflictException(
                'Your piece has gone past the boundaries of the board')

    def _game_not_started_check(self, game):
        """Raise error if all of the pieces for this player and this game have
        been placed already"""
        if game.game_started:
            raise endpoints.ConflictException(
                'All of the pieces for this game have already been placed')

    def _get_all_coords(self,
                        piece_alignment,
                        num_spaces,
                        row_index,
                        col_index):
        """Get all coordinates of the piece based on it's starting coordinates
        and piece size"""
        if piece_alignment == 'vertical':
            columns = [COLUMNS[col_index]]
            rows = ROWS[row_index: row_index + num_spaces]
        elif piece_alignment == 'horizontal':
            columns = COLUMNS[col_index: col_index + num_spaces]
            rows = [ROWS[row_index]]
        else:
            raise endpoints.ConflictException(
                '{} is not a valid piece alignment'.format(piece_alignment))
        return [(col + row) for col in columns for row in rows]

    def _check_placement_validity(self,
                                  game,
                                  player_pieces,
                                  piece_type,
                                  piece_coords):
        """Raise errors if piece placement is invalid:
        if the piece has already been placed,
        or if the piece being placed intersects with another piece"""
        for placed_piece in player_pieces:
            # Raise error if the piece has already been placed on the
            # player's board
            if placed_piece.ship == piece_type:
                raise endpoints.ConflictException(
                    'This piece has already been placed for this player')
            # Raise error if piece intersects with any other piece
            for placed_coordinate in placed_piece.coordinates:
                if placed_coordinate in piece_coords:
                    raise endpoints.ConflictException(
                        'Your piece intersects with {}'
                        .format(placed_coordinate))

    def _update_game_started_status(self, game, player, player_pieces):
        """Checks if all of the pieces for a given player are loaded,
        and if that is true for both of a Game's players, start the game"""
        if len(player_pieces) == len(PIECES):
            if player.key == game.player_one:
                game.player_one_pieces_loaded = True
            else:
                game.player_two_pieces_loaded = True
            # Start game if all pieces for both players have been loaded
            if (game.player_one_pieces_loaded is True and
                    game.player_two_pieces_loaded is True):
                game.game_started = True
            game.put()

    @endpoints.method(request_message=PLACE_PIECE_REQUEST,
                      response_message=PieceDetails,
                      path='game/place_piece/{url_safe_game_key}',
                      name='game.place_piece',
                      http_method='POST')
    def place_piece(self, request):
        """Set up a player's board pieces"""
        piece_type = request.piece_type.name
        first_row_coordinate = request.first_row_coordinate
        first_column_coordinate = request.first_column_coordinate.upper()
        piece_alignment = request.piece_alignment.name
        player_name = request.player_name
        url_safe_game_key = request.url_safe_game_key

        # Raise errors if the row or column coordinates are not valid
        self._coords_validity_check(first_row_coordinate,
                                    first_column_coordinate)

        num_spaces = PIECES[piece_type]['spaces']
        row_index = ROWS.index(first_row_coordinate)
        col_index = COLUMNS.index(first_column_coordinate)

        # Raise errors if the peice is being placed outside
        # of the bounds of the board
        self._board_boundaries_check(piece_alignment,
                                     num_spaces,
                                     row_index,
                                     col_index)

        # Get all coordinates of the piece based on it's
        # starting coordinates and piece size
        coordinates = self._get_all_coords(piece_alignment,
                                           num_spaces,
                                           row_index,
                                           col_index)

        game = get_by_urlsafe(url_safe_game_key, Game)

        # Raise error if all of the pieces for this player
        # and this game have been placed already
        self._game_not_started_check(game)

        player = self._get_registered_player(game, player_name)
        player_pieces = Piece.query(Piece.game == game.key).filter(
            Piece.player == player.key).fetch()

        # Errors based on player's previously placed pieces for this game
        self._check_placement_validity(game,
                                       player_pieces,
                                       piece_type,
                                       coordinates)

        piece = Piece(game=game.key,
                      player=player.key,
                      ship=piece_type,
                      coordinates=coordinates)
        player_pieces.append(piece)
        piece.put()

        # Check if all pieces for this player & game have been placed
        self._update_game_started_status(game, player, player_pieces)

        return self._piece_details_to_form(game, player, piece)

# - - - - Strike Coord Methods  - - - - - - - - - - - - - - - - - - - - - - - -

    def _copy_move_details_to_form(self, index, move):
        move_details_form = MoveDetails()
        setattr(move_details_form, "target_player_name",
                move['target_player'])
        setattr(move_details_form, "attacking_player_name",
                move['attacking_player'])
        setattr(move_details_form, "target_coordinate",
                move['target_coordinate'])
        setattr(move_details_form, "status",
                move['status'])
        setattr(move_details_form, "move_number",
                index + 1)
        if 'ship_type' in move:
            setattr(move_details_form, "ship_type",
                    move['ship_type'])
        return move_details_form

    def _game_over_check(self, game):
        """Check if game has already ended"""
        if game.game_over is True:
            raise endpoints.ConflictException(
                'This game has already ended')

    def _game_started_check(self, game):
        """Ensure game has started"""
        if game.game_started is False:
            raise endpoints.ConflictException(
                '''This game has not started yet,
                all the pieces must first be loaded by both players''')

    def _not_self_strike_check(self, game, target_player):
        """"Ensure the player who's turn it is to strike is
        not the one being struck"""
        if game.player_turn == target_player.key:
            raise endpoints.ConflictException(
                'It is {}\'s turn to strike'.format(target_player.name))

    def _coord_validity_check(self, coord):
        """Ensure passed in coordinate is a valid coordinate
        for the Game Board"""
        if coord not in GRID:
            raise endpoints.ConflictException(
                '{} is not a valid coordinate'.format(coord))

    def _double_hit_check(self, pieces, target_coord):
        """Check for ensuring a coordinate that has
        already been hit is not being hit again"""
        pieces_hit_coords = [piece.hit_marks for piece in pieces]
        for hit_coords in pieces_hit_coords:
            if target_coord in hit_coords:
                raise endpoints.ConflictException(
                    'This coordinate has already been hit')

    def _double_miss_check(self, game, target_player, target_coord):
        """Ensure that the coordinate being struck has not previsouly
        been attempted and missed against target player for given game"""
        misses = Miss.query(Miss.game == game.key).filter(
            Miss.target_player == target_player.key).fetch()
        miss_coords = [missCoord.coordinate for missCoord in misses]
        if target_coord in miss_coords:
            raise endpoints.ConflictException(
                'This coordinate has already been struck and missed')

    def _change_player_turn(self, game):
        """Changes game's current player to the other registered player"""
        if game.player_turn == game.player_one:
            game.player_turn = game.player_two
        else:
            game.player_turn = game.player_one
        game.put()

    def _game_over_status(self, game, target_player):
        target_player_pieces = Piece.query(Piece.game == game.key).filter(
            Piece.player == target_player.key).fetch()
        for piece in target_player_pieces:
            if piece.sunk is False:
                return game.game_over
        game.game_over = True
        game.put()
        return game.game_over

    def _piece_sunk_status(self, piece):
        if sorted(piece.coordinates) == sorted(piece.hit_marks):
            piece.sunk = True
            piece.put()
        return piece.sunk

    def _log_history(self,
                     game,
                     target_player,
                     attacking_player,
                     coord,
                     status,
                     piece_name=None):
        move_details = {'target_player': target_player.name,
                        'attacking_player': attacking_player.name,
                        'target_coordinate': coord,
                        'status': status}
        if piece_name:
            move_details['ship_type'] = piece_name
        game.history.append(move_details)
        game.put()
        return move_details

    @endpoints.method(request_message=STRIKE_REQUEST,
                      response_message=MoveDetails,
                      path='game/strike/{url_safe_game_key}',
                      name='game.strike_coordinate',
                      http_method='POST')
    def strike_coord(self, request):
        """Make a move to strike a given coordinate"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)

        # Check if game has already ended
        self._game_over_check(game)

        # Ensure game has started
        self._game_started_check(game)

        attacking_player = game.player_turn.get()
        target_player = self._get_registered_player(game,
                                                    request.target_player)

        # Ensure attacking_player and target_player are NOT the same
        self._not_self_strike_check(game, target_player)

        target_coord = request.coordinate.upper()

        self._coord_validity_check(target_coord)

        target_player_pieces = Piece.query(Piece.game == game.key).filter(
            Piece.player == target_player.key).fetch()

        # Ensure a coordinate that has been
        # previously hit is not being hit again
        self._double_hit_check(target_player_pieces, target_coord)

        # Coordinates that have been previously attempted and
        # missed against target player
        self._double_miss_check(game, target_player, target_coord)

        # Change it to the other player's turn
        self._change_player_turn(game)

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
                    move_details = self._log_history(
                        game,
                        target_player,
                        attacking_player,
                        target_coord,
                        'Hit - Sunk Ship: Game Over',
                        piece_name=piece.ship)
                elif piece_sunk:
                    move_details = self._log_history(game,
                                                     target_player,
                                                     attacking_player,
                                                     target_coord,
                                                     'Hit - Sunk Ship',
                                                     piece_name=piece.ship)
                else:
                    move_details = self._log_history(game,
                                                     target_player,
                                                     attacking_player,
                                                     target_coord,
                                                     'Hit',
                                                     piece_name=piece.ship)
                return self._copy_move_details_to_form(len(game.history) - 1,
                                                       move_details)

        # If no ship is hit
        move_details = self._log_history(game,
                                         target_player,
                                         attacking_player,
                                         target_coord,
                                         'Miss')
        Miss(game=game.key,
             target_player=target_player.key,
             coordinate=target_coord).put()

        return self._copy_move_details_to_form(len(game.history) - 1,
                                               move_details)

# - - - - Info Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _copy_ranking_to_form(self, index, user_scores):
        ranking_form = Ranking()
        setattr(ranking_form, "username", user_scores[0])
        setattr(ranking_form, "ranking", index + 1)
        setattr(ranking_form, "games_won", user_scores[1])
        setattr(ranking_form, "games_lost", user_scores[2])
        setattr(ranking_form, "score", user_scores[3])
        return ranking_form

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=GameStatusMessage,
                      path='game/status/{url_safe_game_key}',
                      name='game.get_game_status',
                      http_method='GET')
    def get_game_status(self, request):
        """Get a game's current status"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        return self._copy_game_to_form(game)

# - - - - Extended Methods  - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _win_loss_list(self, games):
        """Returns a dict of wins and losses for each user by querying a
        list of all games with status game_over == True"""
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
            if total_games <= 1:
                score = win_diff / total_games
            else:
                score = ((win_diff / total_games) +
                        (log(games_played, total_games)))
            rankings[user]['score'] = score
        return rankings

    def _sort_rankings(self, rankings):
        """Takes in in a dict of rankings, return list of tuples with
        username, wins, losses, score; sorted by score"""
        ranking_list = []
        for user in rankings:
            wins = rankings[user]['won']
            losses = rankings[user]['lost']
            score = rankings[user]['score']
            ranking_list.append((user, wins, losses, score))
        # Good ol' martian smiley:
        # http://stackoverflow.com/questions/3705670/best-way-to-create-a-reversed-list-in-python
        return sorted(ranking_list, key=lambda tup: tup[3])[::-1]

    @endpoints.method(request_message=USER_GAMES_REQUEST,
                      response_message=UserGames,
                      path='user/games/{user_name}',
                      name='game.get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of a User's active games"""
        # it might make sense for each game to be a descendant of a User
        user = self._get_user(request.user_name)
        user_games = Game.query(ndb.OR(Game.player_one == user.key,
                                       Game.player_two == user.key))

        if (request.include is not None and
           request.include.lower() in ['wins', 'losses']):
            if request.include.lower() == 'wins':
                user_games = user_games.filter(
                    Game.winner == user.key).fetch()
            elif request.include.lower() == 'losses':
                user_games = user_games.filter(
                    Game.winner != user.key).filter(
                    Game.winner is not None).fetch()
        else:
            user_games = user_games.fetch()
        return UserGames(games=[self._copy_game_to_form(game)
                         for game in user_games])

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
        completed_games = Game.query().filter(Game.game_over is True).fetch()
        total_games = len(completed_games)
        if total_games == 0:
            raise endpoints.ConflictException('No games have been played')
        win_loss = self._win_loss_list(completed_games)
        rankings = self._assign_rankings(win_loss, total_games)
        sorted_rankings = self._sort_rankings(rankings)
        return Rankings(rankings=[self._copy_ranking_to_form(index, score)
                        for index, score in enumerate(sorted_rankings)])

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=GameHistory,
                      path='game/history/{url_safe_game_key}',
                      name='game.get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Gets history of all moves played for a given game"""
        game_history = get_by_urlsafe(request.url_safe_game_key, Game).history
        return GameHistory(moves=[self._copy_move_details_to_form(index, move)
                           for index, move in enumerate(game_history)])

    @staticmethod
    def _cache_average_moves():
        """Populates memcache with the average number of moves per Game"""
        games = Game.query(Game.game_over is True).fetch()
        num_games = len(games)
        sum_history = 0
        for game in games:
            if game.game_history:
                sum_history += len(game.game_history)
        average = float(sum_history) / num_games
        memcache.set(key='MOVES_PER_GAME',
                     value='The average moves per game is {:.2f}'
                     .format(average))


api = endpoints.api_server([BattleshipAPI])
