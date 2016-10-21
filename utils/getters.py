"""File for retrieving enteties and properties from datastore."""

from google.appengine.ext import ndb
import endpoints

from models.ndbModels import Game, User, Piece, Miss
from utils.validators import check_player_registered, check_piece_alignment
from board import COLUMNS, ROWS


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def get_user(username):
    """Takes in the name of a player/user,
    and returns a user query object"""
    user = User.query(User.name == username).get()
    if not user:
        raise endpoints.ConflictException(
            '{} does not exist.'.format(username))
    return user


def get_registered_player(game, username):
    player = get_user(username)
    check_player_registered(game, player)
    return player


def get_players_pieces(game, player):
    return Piece.query(Piece.game == game.key).filter(
        Piece.player == player.key).fetch()


def get_all_coords(piece_alignment,
                   num_spaces,
                   row_index,
                   col_index):
    """Get all coordinates of the piece based on it's starting coordinates
    and piece size"""
    check_piece_alignment(piece_alignment)
    if piece_alignment == 'vertical':
        columns = [COLUMNS[col_index]]
        rows = ROWS[row_index: row_index + num_spaces]
    elif piece_alignment == 'horizontal':
        columns = COLUMNS[col_index: col_index + num_spaces]
        rows = [ROWS[row_index]]
    return [(col + row) for col in columns for row in rows]


def get_users_active_games(user):
    """Gets all games that a user has joined,
    either as player one or player two"""
    user_games = Game.query(ndb.OR(Game.player_one == user.key,
                                   Game.player_two == user.key))
    active_games = user_games.filter(Game.game_over == False).fetch()
    return active_games


def get_misses_on_player(game, player):
    return Miss.query(Miss.game == game.key).filter(
        Miss.target_player == player.key)


def get_stripped_coord(coord):
    column = ''.join([i for i in coord if not i.isdigit()])
    row = ''.join([i for i in coord if i.isdigit()])
    return column, row


def get_board_state(game, player):
    player_pieces = get_players_pieces(game, player)

    player_board = {}
    for col in COLUMNS:
        player_board[col] = ["E" for i in range(0, len(ROWS))]

    misses_on_player = get_misses_on_player(game, player)

    for miss in misses_on_player:
        miss_col, miss_row = get_stripped_coord(miss.coordinate)
        player_board[miss_col][int(miss_row) - 1] = "M"

    for p in player_pieces:
        p_coords = p.coordinates
        for p_coord in p_coords:
            p_col, p_row = get_stripped_coord(p_coord)
            player_board[p_col][int(p_row) - 1] = "O"

        p_hit_coords = p.hit_marks
        for p_hit_coord in p_hit_coords:
            p_hit_coord_col, p_hit_coord_row = get_stripped_coord(
                p_hit_coord)
            player_board[p_hit_coord_col][int(p_hit_coord_row) - 1] = "X"

    return player_board
