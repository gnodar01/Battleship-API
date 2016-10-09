# Battleship API

## Using API explorer

You will need to launch Google Chrome from terminal with the flag `--user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:[Port Number]`

For example (whilst quit from google chrome): 
```
Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080
```

To navigate to the Google API explorer on the appspot domain, go to `https://[your project id].appspot.com/_ah/api/explorer`

For example:

```
https://nodar-battle-ship.appspot.com/_ah/api/explorer
```

To navigate to the Google API explorer on localhost, go to `http://localhost:[Port Number]/_ah/api/explorer`

For example:
  
```
http://localhost:8080/_ah/api/explorer
```

## Battleship Play

The board is 10 x 10
- Columns A - J
- Rows 1 - 10

```
----------------------------------------------
|----| A | B | C | D | E | F | G | H | I | J |
----------------------------------------------
| 1  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 2  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 3  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 4  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 5  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 6  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 7  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 8  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 9  | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
| 10 | . | . | . | . | . | . | . | . | . | . |
----------------------------------------------
```

There are 5 pieces

- One 5 space ship - An Aircraft Carrier: `| O | O | O | O | O |`

- One 4 space ship - A Battleship: `| O | O | O | O |`

- Two 3 space ships - A Submarine + A Destroyer: `| O | O | O |` + `| O | O | O |`

- One 2 space ship - A Patrol Ship: `| O | O |`

Exactly two players start and join a game. They must each load their own boards with each of the 5 pieces. Once all pieces, for both players, are loaded, they may begin the game. The player who's turn it is, must guess a coordinate, A1 - J10. If the coordinate the player guesses, contains a ship, that ship is struck. To completely sink a ship, a player must hit each of the available spaces belonging to that ship. After the player makes a move, it is then the other player's turn to guess a coordinate. The first player to sink all 5 of the opposite player's ships wins.

## Instructions for using the Battleship API

- To begin a game, there must be at least two players. To create a user account, you must send a `POST` request to the `user.create_user` endpoint at `/user/new`. `user.create_user` takes in an `email` field and `name` field, both of which are *Strings*.

- To create a new game, a `POST` request is sent to the `game.create_game` endpoint at `/game/new`. This endpoint takes in two fields: `player_one_name`, which is required, and `player_two_name`, which is optional (a second player may join an open game at a later time). Both fields must be supplied with the usernames of registered users.

- If a game was created with only one player, the `game.join_game` endpoint may be utilized at `/game/join/[game`s url-safe key]`. This endpoint takes one field, `player_two_name`, a *string* of the name from a registered user.

- To cancel a game, the `game.cancel_game` endpoint may be utilized at `/game/cancel/[game's url-safe key]` with a `GET` request. This endpoint takes in no fields. Once a game is cancelled, the game and all corresponding entities such as pieces and game history will be deleted.

- To get the current status of a particular game, send a `GET` request to the `game.get_game_status` endpoint at `/game/status/[games' url-safe key]`. `game.get_game_status` takes no fields.

- Once a game has two players assigned to it, pieces may be placed on the player's respective boards. To do this, send a `POST` request to the `game.place_piece` endpoint at `/game/place_piece/[games' url-safe key]`. Once all the pieces for both players have been placed, the games `game_started` status is set to 'True'. This endpoint takes 5 required fields:
  - `player_name` is the user that the piece is being placed for. This user must be registered to the game that the url-safe key in teh url refers to.
  - `piece_type` is the ship type being placed. The ship types include 'aircraft_carrier', 'battleship', 'submarine', 'destroyer', and 'patrol_ship'. No other input will be accepted.
  - `piece_alignment` is the alignment of the ship piece on the game board. It may be 'vertcial' (ship takes up multiple rows) or 'horizontal' (ship takes up multiple columns). No other input will be accepted.
  - `first_column_coordinate` is the column of the first coordinate the ship is being placed on. It may be any letter from 'A' to 'J'. No other letter may be used.
  - `first_row_coordinate` is the row of the first coordinate the ship is being placed on. It may be any number from '1' - '10'. No other number may be used.

- Once all pieces for a game have been placed, the game's `game_started` is set to 'True'. The game's two players can then begin to strike each other's boards. The game's `player_turn` referes to the player whos turn it is to attack the other player's board. `player_turn` is always set to `player_one` when a game first begins. To strike a player's board, a `POST` request should be sent to the `game.strike_coordinate` endpoint at `/game/strike/[game's url-safe key]`. The endpoint takes 2 fields:
  - `target_player` is the player who's board is being attacked.
  - `coordinate` is the coordiante being attacked. It must be a coordinate from "A1" to "J10". No other coordinate may be used.

  Once a coordinate is struck, the game's `player_turn` is set to the opposite player. That player may then strike then strike back. Once all of the spaces for a given ship are hit, that ship's `sunk` status is set to 'True'. The first player to sink all of the other player's ships wins the game. The game's `game_over` status is then set to 'True', and the game's `winner` is set to the winning player's name.

- To get a list of a user's games, a `GET` request may be sent to the `game.get_user_games` at `/user/games/[registered user's name]`. The endpoint url also takes an optional `include` query parameter, which may be set to 'wins' or 'losses'. If set to 'wins', only games that the user has won will be returned. If set to 'losses', only games that the user has lost will be returned.

- All moves during a game are recorded. To get a history of all of the moves made in a game, a `GET` request may be sent to the `game.get_game_history` endpoint at `/game/history/[game's url-safe key]`.

- To get the current rankings of all users, a `GET` request should be sent to the `get_rankings` endpoint, at `/rankings`.

### Scoring

The scores used to calculate the rankings of all users are dynamically assigned and take into account the number of games won, the number of games lost, and the number of games played. The formula used is ((games won - games lost) divided by (/) the total number of games played) plus (+) (the log, with a base of of the total number of games played overall, of total games the user has played).The first half of the formula used is the difference between wins and losses of the games the user has played to completion (games won - games lost) as a percent of the total number of games completed amongst all users. This means that when comparing user scores only the number of wins, *above* the number of losses, will work towards your score. In other words, if you have more losses than wins, this will be negative, and vice versa. So, the absolute maximum this can be is +1.0, and the absolute minimum is -1.0. While this takes into account how well a user plays (given by a high win rate against loss rate), it does not take into account how frequently a user plays, which is important. For example with just the first half of the formula, a user with 1 win, and 0 losses, is ranked the exact same as a user with 100 wins, and 99 losses. To reward players that have played a greater of number of games, the first half of the formula is added to the second half: log, with base of total games played overall, of total games played by user. While this is a constantly changing value, based on the number of games played overall, it ensures that users that play frequently are not outranked by users that have high win counts for a relatively low amount of games.


## Endpoint Details

### API Endpoint

https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1


- battleship.user.create_user
  - Request type: `POST`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/user/new`
  - Request fields:
    - `name`
    - `email`
  - Response fields:
    - `name`: "[player's name]"
    - `email`: "[Player's e-mail]"


- battleship.game.create_game
  - Request type: `POST`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/new`
  - Request fields:
    - `player_one_name` - must be a registered user
    - `player_two_name` - *Opitional*, must be a registered user
  - Response fields:
    - `player_one`: "[player one's name]"
    - `player_two`: "[player two's name]", if provided, or "None"
    - `player_one_pieces_loaded`: "False"
    - `player_two_pieces_loaded`: "False"
    - `game_started`: "False"
    - `player_turn`: "[Player one's name]"
    - `game_over`: "False"
    - `winner`: "None"
    - `game_key`: "[URL-safe game key]" (This should be stored, as it is the unique identifier needed to make any subsequent requests regarding this game specificially)


- battleship.game.join_game
  - Request type: `POST`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/join/[game's url-safe key]`
  - Request fields:
    - `player_two_name`: must be a registered user
  - Response fields:
    - `player_one`: "[player one's name]"
    - `player_two`: "[player two's name]"
    - `player_one_pieces_loaded`: "False"
    - `player_two_pieces_loaded`: "False"
    - `game_started`: "False"
    - `player_turn`: "[Player one's name]"
    - `game_over`: "False"
    - `winner`: "None"
    - `game_key`: "[URL-safe game key]"


- battleship.game.cancel_game
  - Request Type: `GET`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/cancel/[game's url-safe key]`
  - Request Fields:
    - None
  - Response Fields:
    - `message`: "Game deleted"


- battleship.game.get_game_status
  - Request Type: `GET`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/status/[game's url-safe key]`
  - Request Fields:
    - None
  - Response Fields:
    - `player_one`: "[player one's name]"
    - `player_two`: "[player two's name]"
    - `player_one_pieces_loaded`
      - "True"
      - "False"
    - `player_two_pieces_loaded`
      - "True"
      - "False"
    - `game_started`
      - "True"
      - "False"
    - `player_turn`: "[Player one's name]"
    - `game_over`
      - "True"
      - "False"
    - `winner`: "[user who won game]" or "None"
    - `game_key`: "[URL-safe game key]"


- battleship.game.place_piece
  - Request Type: `POST`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/place_piece/[game's url-safe key]`
  - Request Fields:
    - `player_name` - must be registered user
    - `piece_type` - lowercase only
      - "aircraft_carrier"
      - "battleship"
      - "submarine"
      - "destroyer"
      - "patrol_ship"
    - `piece_alignment` - lowercase only
      - "horizontal"
      - "vertical"
    - `first_column_coordinate`
      - "A" - "J"
    - `first_row_coordinate` - uppercase only
      - "1" - "10"
  - Response Fields:
    - `game_key` - game's url-safe key
    - `owner` - "[player's name]"
    - `ship_type`
      - "aircraft_carrier"
      - "battleship"
      - "submarine"
      - "destroyer"
      - "patrol_ship"
    - `coordinates` - *Array*
      - `coordinate`
        - "A1" - "J10"


- battleship.game.strike_coordinate
  - Request Type: `POST`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/strike/[game's url-safe key]`
  - Request Fields:
    - `target_player`: "[name of user registered to game opposite of player attacking]"
    - `coordinate`
      - "A1" - "J10"
  - Response Fields:
    - `target_player_name`: "[name of user being attacked]"
    - `attacking_player_name`: "[name of attacking user]"
    - `target_coordinate`
      - "A1" - "J10"
    - `status`
      - "Hit"
      - "Hit - Sunk Ship"
      - "Hit - Sunk Ship: Game Over"
      - "Miss"
    - `ship_type`
      - "aircraft_carrier"
      - "battleship"
      - "submarine"
      - "destroyer"
      - "patrol_ship"
    - `move_number` - *Integer*


- battleship.game.get_user_games
  - Request Type: `GET`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/user/games/[registered user's name]?include=[Optional: wins or losses]`
  - Request Fields:
    - None
  - Response Fields:
    - `games` - *Array*
      - `player_one`: "[player one's name]"
      - `player_two`: "[player two's name]"
      - `player_one_pieces_loaded`
        - "True"
        - "False"
      - `player_two_pieces_loaded`
        - "True"
        - "False"
      - `game_started`
        - "True"
        - "False"
      - `player_turn`: "[Player one's name]"
      - `game_over`
        - "True"
        - "False"
      - `winner`: "[user who won game]" or "None"
      - `game_key`: "[URL-safe game key]"


- battleship.game.get_game_history
  - Request Type: `GET`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/history/[game's url-safe key]`
  - Request Fields:
    - None
  - Response Fields:
    - `moves` - *Array*
      - `target_player_name`: "[name of user being attacked]"
      - `attacking_player_name`: "[name of attacking user]"
      - `target_coordinate`
        - "A1" - "J10"
      - `status`
        - "Hit"
        - "Hit - Sunk Ship"
        - "Hit - Sunk Ship: Game Over"
        - "Miss"
      - `ship_type`
        - "aircraft_carrier"
        - "battleship"
        - "submarine"
        - "destroyer"
        - "patrol_ship"
      - `move_number` - *Integer*


- battleship.get_rankings
  - Request Type: `GET`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/rankings`
  - Request Fields:
    - None
  - Response Fields:
    - `rankings` - *Array*
      - `username`
      - `ranking` - *Integer*
      - `games_won` - *Integer*
      - `games_lost` - *Integer*
      - `score` - *Float*


