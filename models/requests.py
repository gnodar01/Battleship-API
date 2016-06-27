"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
import endpoints
from datetime import date
from protorpc import messages, message_types
from models.protorpcModels import PieceType, Alignment, Column


class UserRequest(messages.Message):
    user_name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)

class NewGameRequest(messages.Message):
    player_one_name = messages.StringField(1, required=True)
    player_two_name = messages.StringField(2)

class JoinGameRequest(messages.Message):
	game_key = messages.StringField(1, required=True)
	player_two_name = messages.StringField(2)

class PlacePieceRequest(messages.Message):
	game_key = messages.StringField(1)
	player_name = messages.StringField(2)
	piece_type = messages.EnumField(PieceType, 3, required=True) # PieceType can be string
	piece_alignment = messages.EnumField(Alignment, 4, required=True)
	first_row_coordinate = messages.IntegerField(5, required=True)
	first_column_coordinate = messages.EnumField(Column, 6, required=True)




