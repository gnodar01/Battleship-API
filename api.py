# -*- coding: utf-8 -*-`
"""
api.py - Udacity conference server-side Python App Engine API;
            uses Google Cloud Endpoints

    for Fullstack Nanodegree Project

    created by Nodari Gogoberidze - June 2016
"""

from math import log

import endpoints
from protorpc import remote, message_types
from google.appengine.api import memcache

from models.ndbModels import User, Game, Piece, Miss
from models.responses import (
    StringMessage,
    UserForm,
    GameStatusMessage,
    UserGames,
    PieceDetails,
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

from getters import (
    get_by_urlsafe,
    get_user,
    get_registered_player,
    get_all_coords,
    get_users_active_games
)

from validators import (
    check_email,
    check_username_len,
    check_user_exists,
    check_email_exists,
    check_players_unique,
    check_game_open,
    check_coords_validity,
    check_board_boundaries,
    check_game_not_started,
    check_placement_validity,
    check_game_not_over,
    check_game_started,
    check_not_self_strike,
    check_coord_validity,
    check_not_double_hit,
    check_not_double_miss
)

from populate_form import (
    copy_user_to_form,
    copy_game_to_form,
    copy_piece_details_to_form,
    copy_move_details_to_form,
    copy_ranking_to_form
)

from board import (
    PIECES,
    COLUMNS,
    ROWS
)


# TODO: Authentication for each of the methods
@endpoints.api(name='battle_ship', version='v1')
class BattleshipAPI(remote.Service):
    """Battle Ship API"""

# - - - - User Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(request_message=UserRequest,
                      response_message=UserForm,
                      path='user/new',
                      name='user.create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        check_email(request.email)
        check_username_len(request.user_name)
        check_user_exists(request.user_name)
        check_email_exists(request.email)

        user = User(name=request.user_name, email=request.email)
        user.put()
        return copy_user_to_form(user)

# - - - - Game Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(request_message=NewGameRequest,
                      response_message=GameStatusMessage,
                      path='game/new',
                      name='game.create_game',
                      http_method='POST')
    def create_game(self, request):
        """Create a new Game"""
        check_players_unique(request.player_one_name, request.player_two_name)
        player_one = get_user(request.player_one_name)

        if request.player_two_name:
            player_two = get_user(request.player_two_name)
            game = Game(player_one=player_one.key,
                        player_turn=player_one.key,
                        player_two=player_two.key)
        else:
            game = Game(player_one=player_one.key, player_turn=player_one.key)
        game.put()
        return copy_game_to_form(game)

    @endpoints.method(request_message=JOIN_GAME_REQUEST,
                      response_message=GameStatusMessage,
                      path='game/join/{url_safe_game_key}',
                      name='game.join_game',
                      http_method='PUT')
    def join_game(self, request):
        """Join a game if not already full"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)

        check_game_open(game)

        player_two = get_user(request.player_two_name)
        player_one = game.player_one.get()

        check_players_unique(player_one.name, player_two.name)

        game.player_two = player_two.key
        game.put()
        return copy_game_to_form(game)

# - - - - Place piece methods - - - - - - - - - - - - - - - - - - - - - - - - -

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
        check_coords_validity(first_row_coordinate, first_column_coordinate)

        num_spaces = PIECES[piece_type]['spaces']
        row_index = ROWS.index(first_row_coordinate)
        col_index = COLUMNS.index(first_column_coordinate)

        # Raise errors if the peice is being placed outside
        # of the bounds of the board
        check_board_boundaries(piece_alignment,
                               num_spaces,
                               row_index,
                               col_index)

        # Get all coordinates of the piece based on it's
        # starting coordinates and piece size
        coordinates = get_all_coords(piece_alignment,
                                     num_spaces,
                                     row_index,
                                     col_index)

        game = get_by_urlsafe(url_safe_game_key, Game)

        # Raise error if all of the pieces for this player
        # and this game have been placed already
        check_game_not_started(game)

        player = get_registered_player(game, player_name)
        player_pieces = Piece.query(Piece.game == game.key).filter(
            Piece.player == player.key).fetch()

        # Errors based on player's previously placed pieces for this game
        check_placement_validity(game,
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

        return copy_piece_details_to_form(game, player, piece)

# - - - - Strike Coord Methods  - - - - - - - - - - - - - - - - - - - - - - - -

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
        check_game_not_over(game)

        # Ensure game has started
        check_game_started(game)

        attacking_player = game.player_turn.get()
        target_player = get_registered_player(game,
                                              request.target_player)

        # Ensure attacking_player and target_player are NOT the same
        check_not_self_strike(game, target_player)

        target_coord = request.coordinate.upper()

        check_coord_validity(target_coord)

        target_player_pieces = Piece.query(Piece.game == game.key).filter(
            Piece.player == target_player.key).fetch()

        # Ensure a coordinate that has been
        # previously hit is not being hit again
        check_not_double_hit(target_player_pieces, target_coord)

        # Coordinates that have been previously attempted and
        # missed against target player
        check_not_double_miss(game, target_player, target_coord)

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
                return copy_move_details_to_form(len(game.history) - 1,
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

        return copy_move_details_to_form(len(game.history) - 1,
                                         move_details)

# - - - - Info Methods  - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=GameStatusMessage,
                      path='game/status/{url_safe_game_key}',
                      name='game.get_game_status',
                      http_method='GET')
    def get_game_status(self, request):
        """Get a game's current status"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        return copy_game_to_form(game)

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
        user = get_user(request.user_name)
        active_games = get_users_active_games(user)
        return UserGames(games=[copy_game_to_form(game)
                         for game in active_games])

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{url_safe_game_key}',
                      name='game.cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancels an active game"""
        game = get_by_urlsafe(request.url_safe_game_key, Game)
        if game.game_over is False:
            game_pieces = Piece.query(Piece.game == game.key).fetch()
            game_misses = Miss.query(Miss.game == game.key).fetch()
            for piece in game_pieces:
                piece.key.delete()
            for miss in game_misses:
                miss.key.delete()
            game.key.delete()
            return StringMessage(message="Game deleted")
        else:
            raise endpoints.ConflictException(
                'Cannot cancel game that has already ended.')

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=Rankings,
                      path='rankings',
                      name='get_rankings',
                      http_method='GET')
    def get_user_ranks(self, request):
        """Gets list of user rankings"""
        completed_games = Game.query().filter(Game.game_over == True).fetch()
        total_games = len(completed_games)
        if total_games == 0:
            raise endpoints.ConflictException('No games have been played')
        win_loss = self._win_loss_list(completed_games)
        rankings = self._assign_rankings(win_loss, total_games)
        sorted_rankings = self._sort_rankings(rankings)
        return Rankings(rankings=[copy_ranking_to_form(index, score)
                        for index, score in enumerate(sorted_rankings)])

    @endpoints.method(request_message=GAME_REQUEST,
                      response_message=GameHistory,
                      path='game/history/{url_safe_game_key}',
                      name='game.get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Gets history of all moves played for a given game"""
        game_history = get_by_urlsafe(request.url_safe_game_key, Game).history
        return GameHistory(moves=[copy_move_details_to_form(index, move)
                           for index, move in enumerate(game_history)])

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
                     value='The average moves per game is {:.2f}'
                     .format(average))


api = endpoints.api_server([BattleshipAPI])
