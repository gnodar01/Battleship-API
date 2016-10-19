"""File for retrieving enteties and properties from datastore."""

from google.appengine.ext import ndb
import endpoints

from models.ndbModels import Game, User
from validators import check_player_registered, check_piece_alignment
from api import COLUMNS, ROWS


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
