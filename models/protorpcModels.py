"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages, message_types


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class GameStatusMessage(messages.Message):
    """GameStatus-- outbound message describing a given game's current status"""
    player_one = messages.StringField(1, required=True)
    player_two = messages.StringField(2, required=True)
    player_one_pieces_loaded = messages.StringField(3, required=True)
    player_two_pieces_loaded = messages.StringField(4, required=True)
    game_started = messages.StringField(5, required=True)
    player_turn = messages.StringField(6, required=True)
    game_over = messages.StringField(7, required=True)

class PieceType(messages.Enum):
    aircraft_carrier = 1
    battleship = 2
    submarine = 3
    destroyer = 4
    patrol_ship = 5

class Alignment(messages.Enum):
    horizontal = 1
    vertical = 2
