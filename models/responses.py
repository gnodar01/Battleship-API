from protorpc import messages


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """Information for user"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)


class GameStatusMessage(messages.Message):
    """GameStatus-- outbound message describing
    a given game's current status"""
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


class Coordinate(messages.Message):
    coordinate = messages.StringField(1, required=True)


class PieceDetails(messages.Message):
    """Details for a placed piece"""
    game_key = messages.StringField(1, required=True)
    owner = messages.StringField(2, required=True)
    ship_type = messages.StringField(3, required=True)
    coordinates = messages.MessageField(Coordinate, 4, repeated=True)


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


class CoordStatus(messages.Enum):
    """Coord Status"""
    empty = 1
    occupied = 2
    miss = 3
    hit = 4


class CoordInfo(messages.Message):
    """Columns"""
    column = messages.StringField(1, required=True)
    row = messages.StringField(2, required=True)
    value = messages.EnumField(CoordStatus, 3)


class MoveDetails(messages.Message):
    """Details of a given move"""
    target_player_name = messages.StringField(1, required=True)
    attacking_player_name = messages.StringField(2, required=True)
    target_coordinate = messages.StringField(3, required=True)
    status = messages.StringField(4, required=True)
    ship_type = messages.StringField(5)
    move_number = messages.IntegerField(6, required=True)
    target_player_board_state = messages.MessageField(CoordInfo,
                                                      7,
                                                      repeated=True)
    attacking_player_board_state = messages.MessageField(CoordInfo,
                                                         8,
                                                         repeated=True)


class GameHistory(messages.Message):
    """History of all moves played for a given game"""
    moves = messages.MessageField(MoveDetails, 1, repeated=True)
