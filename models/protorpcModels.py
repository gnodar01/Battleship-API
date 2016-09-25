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
    game_key = messages.StringField(8, required=True)
    winner = messages.StringField(9, required=True)

class UserGames(messages.Message):
    """GamesStatusMessages on each of a user's games"""
    games = messages.MessageField(GameStatusMessage, 1, repeated=True)

class Ranking(messages.Message):
    """Ranking for a user"""
    username = messages.StringField(1, required=True)
    ranking = messages.IntegerField(2, required=True)
    games_won = messages.IntegerField(3, required=True)
    games_lost = messages.IntegerField(4, required=True)
    score = messages.FloatField(5, required=True)

class Rankings(messages.Message):
    """Rankings for each user"""
    rankings = messages.MessageField(Ranking, 1, repeated=True)

class MoveDetails(messages.Message):
    """Details of a given move"""
    target_player_name = messages.StringField(1, required=True)
    attacking_player_name = messages.StringField(2, required=True)
    target_coordinate = messages.StringField(3, required=True)
    status = messages.StringField(4, required=True)
    ship_type = messages.StringField(5)
    move_number = messages.IntegerField(6, required=True)

class GameHistory(messages.Message):
    """History of all moves played for a given game"""
    moves = messages.MessageField(MoveDetails, 1, repeated=True)
