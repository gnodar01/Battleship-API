from models.responses import (
    UserForm,
    GameStatusMessage,
    PieceDetails,
    Coordinate,
    MoveDetails
)


def _copy_user_to_form(user_obj):
    user_form = UserForm()
    setattr(user_form, 'name', getattr(user_obj, 'name'))
    setattr(user_form, 'email', getattr(user_obj, 'email'))
    return user_form


def copy_game_to_form(game_obj):
    game_form = GameStatusMessage()

    setattr(game_form, "game_key", str(game_obj.key.urlsafe()))

    for field in game_form.all_fields():
        if (field.name == "player_one" or field.name == "player_two" or
                field.name == "player_turn" or field.name == "winner"):

            player_key = getattr(game_obj, field.name)

            if player_key:
                player = player_key.get()
                setattr(game_form, field.name, player.name)
            else:
                setattr(game_form, field.name, "None")

        elif hasattr(game_obj, field.name):
            setattr(game_form, field.name,
                    str(getattr(game_obj, field.name)))

    return game_form


def piece_details_to_form(game, user, piece):
    piece_form = PieceDetails()
    setattr(piece_form, 'game_key', game.key.urlsafe())
    setattr(piece_form, 'owner', user.name)
    setattr(piece_form, 'ship_type', piece.ship)
    setattr(piece_form, 'coordinates',
            [Coordinate(coordinate=coord) for coord in piece.coordinates])
    return piece_form


def copy_move_details_to_form(index, move):
    move_details_form = MoveDetails()
    setattr(move_details_form, "target_player_name",
            move['target_player'])
    setattr(move_details_form, "attacking_player_name",
            move['attacking_player'])
    setattr(move_details_form, "target_coordinate",
            move['target_coordinate'])
    setattr(move_details_form, "status",
            move['status'])
    setattr(move_details_form, "move_number",
            index + 1)
    if 'ship_type' in move:
        setattr(move_details_form, "ship_type",
                move['ship_type'])
    return move_details_form
