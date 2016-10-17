"""models.py - This file contains the class definitions for the Datastore
entities used by the Game."""

from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)


class Game(ndb.Model):
    """Game object for game details and status"""
    player_one = ndb.KeyProperty(required=True, kind='User')
    player_two = ndb.KeyProperty(kind='User')
    player_one_pieces_loaded = ndb.BooleanProperty(required=True,
                                                   default=False)
    player_two_pieces_loaded = ndb.BooleanProperty(required=True,
                                                   default=False)
    game_started = ndb.BooleanProperty(required=True, default=False)
    player_turn = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty(kind='User')
    history = ndb.JsonProperty(repeated=True)


class Piece(ndb.Model):
    """Location and status of player's game pieces"""
    game = ndb.KeyProperty(required=True, kind='Game')
    player = ndb.KeyProperty(required=True, kind='User')
    ship = ndb.StringProperty(required=True)
    coordinates = ndb.StringProperty(repeated=True)
    hit_marks = ndb.StringProperty(repeated=True)
    sunk = ndb.BooleanProperty(required=True, default=False)


class Miss(ndb.Model):
    """Store of all misses"""
    game = ndb.KeyProperty(required=True, kind='Game')
    target_player = ndb.KeyProperty(required=True, kind='User')
    coordinate = ndb.StringProperty(required=True)
