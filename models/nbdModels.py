"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)


class Game(ndb.Model):
    """Game object for game details and status"""
    player_one = ndb.KeyProperty(required=True, kind='User')
    player_two = ndb.KeyProperty(kind='User')
    pieces_loaded = ndb.BooleanProperty(required=True, default=False)
    game_over = ndb.BooleanProperty(required=True, default=False)

class Piece(ndb.Model):
	"""Location and status of player's game pieces"""
	game = ndb.KeyProperty(required=True, kind='Game')
	player = ndb.KeyProperty(required=True, kind='User')
	coordinates = ndb.StringProperty(repeated=True)
	hit_marks = ndb.StringProperty(repeated=True)
	sunk = ndb.BooleanProperty(required=True, default=False)
