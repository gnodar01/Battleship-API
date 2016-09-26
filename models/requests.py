import random
import endpoints
from datetime import date
from protorpc import messages, message_types

class UserRequest(messages.Message):
    user_name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)

class NewGameRequest(messages.Message):
    player_one_name = messages.StringField(1, required=True)
    player_two_name = messages.StringField(2)

class JoinGameForm(messages.Message):
    player_two_name = messages.StringField(1)

class PieceType(messages.Enum):
    aircraft_carrier = 1
    battleship = 2
    submarine = 3
    destroyer = 4
    patrol_ship = 5

class Alignment(messages.Enum):
    horizontal = 1
    vertical = 2

class PlacePieceForm(messages.Message):
    player_name = messages.StringField(1)
    piece_type = messages.EnumField(PieceType, 2, required=True) # PieceType can be string
    piece_alignment = messages.EnumField(Alignment, 3, required=True)
    first_row_coordinate = messages.StringField(4, required=True)
    first_column_coordinate = messages.StringField(5, required=True)

class StrikeForm(messages.Message):
    target_player = messages.StringField(1)
    coordinate = messages.StringField(2)

class PlaceDummyPiecesForm(messages.Message):
    player_one = messages.StringField(1)
    player_two = messages.StringField(2)


GAME_REQUEST = endpoints.ResourceContainer(
    url_safe_game_key = messages.StringField(1, required=True))

JOIN_GAME_REQUEST = endpoints.ResourceContainer(
    JoinGameForm,
    url_safe_game_key = messages.StringField(2, required=True))

PLACE_PIECE_REQUEST = endpoints.ResourceContainer(
    PlacePieceForm,
    url_safe_game_key = messages.StringField(6, required=True))

STRIKE_REQUEST = endpoints.ResourceContainer(
    StrikeForm,
    url_safe_game_key = messages.StringField(3, required=True))

PLACE_DUMMY_PIECES_REQUEST = endpoints.ResourceContainer(
    PlaceDummyPiecesForm,
    url_safe_game_key = messages.StringField(3))

USER_GAMES_REQUEST = endpoints.ResourceContainer(
    user_name = messages.StringField(1, required=True),
    include = messages.StringField(2)
)

