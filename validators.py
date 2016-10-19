import endpoints
from re import match

from models.ndbModels import User
from api import COLUMNS, ROWS, GRID


def check_email(email):
    email_format_match = match(
        r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
        email)
    if not email_format_match:
        raise endpoints.ConflictException('E-mail is not valid')


def check_username_len(username):
    if len(username) < 3:
        raise endpoints.ConflictException(
            'Username must be at least 3 characters')


def check_user_exists(username):
    if User.query(User.name == username).get():
        raise endpoints.ConflictException(
            'A User with that name already exists')


def check_email_exists(email):
    if User.query(User.email == email).get():
        raise endpoints.ConflictException(
            'A User with that E-Mail already exists')


def check_player_registered(game, player):
    if game.player_one != player.key and game.player_two != player.key:
        raise endpoints.ConflictException(
            '{} is not registered for this game'.format(player.name))


def check_players_unique(player_one_name, player_two_name):
    if player_one_name == player_two_name:
        raise endpoints.ConflictException(
            'Player one cannot be the same as player two.')


def check_game_open(game):
    if game.player_two:
        raise endpoints.ConflictException('This game is already full!')


def check_coords_validity(row_coord, col_coord):
    """Raise errors if the row or column coordinates are not valid"""
    if row_coord not in ROWS:
        raise endpoints.ConflictException(
            'Row coordinate must be between 1 - 10')

    if col_coord not in COLUMNS:
        raise endpoints.ConflictException(
            'Column coordinate must be between A - J')


def check_board_boundaries(piece_alignment, num_spaces, row_index, col_index):
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


def check_game_not_started(game):
    """Raise error if all of the pieces for this player and this game have
    been placed already"""
    if game.game_started:
        raise endpoints.ConflictException(
            'All of the pieces for this game have already been placed')


def check_piece_alignment(piece_alignment):
    if piece_alignment not in ['vertical', 'horizontal']:
        raise endpoints.ConflictException(
            '{} is not a valid piece alignment'.format(piece_alignment))


def check_placement_validity(game,
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


def check_game_not_over(game):
    """Check if game has already ended"""
    if game.game_over is True:
        raise endpoints.ConflictException(
            'This game has already ended')


def check_game_started(game):
    """Ensure game has started"""
    if game.game_started is False:
        raise endpoints.ConflictException(
            '''This game has not started yet,
            all the pieces must first be loaded by both players''')


def check_not_self_strike(game, target_player):
    """"Ensure the player who's turn it is to strike is
    not the one being struck"""
    if game.player_turn == target_player.key:
        raise endpoints.ConflictException(
            'It is {}\'s turn to strike'.format(target_player.name))


def check_coord_validity(coord):
    """Ensure passed in coordinate is a valid coordinate
    for the Game Board"""
    if coord not in GRID:
        raise endpoints.ConflictException(
            '{} is not a valid coordinate'.format(coord))


def check_not_double_hit(self, pieces, target_coord):
    """Check for ensuring a coordinate that has
    already been hit is not being hit again"""
    pieces_hit_coords = [piece.hit_marks for piece in pieces]
    for hit_coords in pieces_hit_coords:
        if target_coord in hit_coords:
            raise endpoints.ConflictException(
                'This coordinate has already been hit')
