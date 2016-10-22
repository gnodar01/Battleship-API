from board import COLUMNS, ROWS

from models.responses import (
    UserForm,
    GameStatusMessage,
    PieceDetails,
    Coordinate,
    MoveDetails,
    Ranking,
    CoordInfo,
    CoordStatus
)


def copy_user_to_form(user_obj):
    user_form = UserForm()
    setattr(user_form, 'name', getattr(user_obj, 'name'))
    setattr(user_form, 'email', getattr(user_obj, 'email'))
    return user_form


def copy_game_to_form(game_obj, board_state_forms):
    game_form = GameStatusMessage()

    setattr(game_form, 'game_key', str(game_obj.key.urlsafe()))

    for field in game_form.all_fields():
        if (field.name == 'player_one' or field.name == 'player_two' or
                field.name == 'player_turn' or field.name == 'winner'):

            player_key = getattr(game_obj, field.name)

            if player_key:
                player = player_key.get()
                setattr(game_form, field.name, player.name)
            else:
                setattr(game_form, field.name, 'None')

        elif hasattr(game_obj, field.name):
            setattr(game_form, field.name,
                    str(getattr(game_obj, field.name)))

    setattr(game_form,
            'player_one_board_state',
            board_state_forms['player_one'])

    if board_state_forms['player_two']:
        setattr(game_form,
                'player_two_board_state',
                board_state_forms['player_two'])

    return game_form


def copy_piece_details_to_form(game, user, piece):
    piece_form = PieceDetails()
    setattr(piece_form, 'game_key', game.key.urlsafe())
    setattr(piece_form, 'owner', user.name)
    setattr(piece_form, 'ship_type', piece.ship)
    setattr(piece_form, 'coordinates',
            [Coordinate(coordinate=coord) for coord in piece.coordinates])
    return piece_form


def copy_move_log_to_form(index,
                          move,
                          target_player_board_state,
                          attacking_player_board_state):
    move_log_form = MoveDetails()
    setattr(move_log_form, "target_player_name",
            move['target_player'])
    setattr(move_log_form, "attacking_player_name",
            move['attacking_player'])
    setattr(move_log_form, "target_coordinate",
            move['target_coordinate'])
    setattr(move_log_form, "status",
            move['status'])
    setattr(move_log_form, "move_number",
            index + 1)
    setattr(move_log_form, "target_player_board_state",
            target_player_board_state)
    setattr(move_log_form, "attacking_player_board_state",
            attacking_player_board_state)
    if 'ship_type' in move:
        setattr(move_log_form, "ship_type",
                move['ship_type'])
    return move_log_form


def copy_ranking_to_form(index, user_scores):
    ranking_form = Ranking()
    setattr(ranking_form, "username", user_scores[0])
    setattr(ranking_form, "ranking", index + 1)
    setattr(ranking_form, "games_won", user_scores[1])
    setattr(ranking_form, "games_lost", user_scores[2])
    setattr(ranking_form, "score", user_scores[3])
    return ranking_form


def copy_board_state_to_form(board_state):
    board_state_form = []
    for col in COLUMNS:
        for row in ROWS:
            coord_info_form = CoordInfo(column=col, row=row)
            coord_status = board_state[col][int(row) - 1]
            if coord_status == 'E':
                setattr(coord_info_form, 'value', CoordStatus('empty'))
            elif coord_status == 'O':
                setattr(coord_info_form, 'value', CoordStatus('occupied'))
            elif coord_status == 'M':
                setattr(coord_info_form, 'value', CoordStatus('miss'))
            elif coord_status == 'X':
                setattr(coord_info_form, 'value', CoordStatus('hit'))
            board_state_form.append(coord_info_form)
    return board_state_form
