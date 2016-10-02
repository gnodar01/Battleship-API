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

- To create a new game, a `POST` request is sent to the `game.create_game` endpoint at `game/new`. `game/new` takes in two fields: `player_one_name`, which is required, and `player_two_name`, which is optional (a second player may join an open game at a later time). Both fields must be supplied with the usernames of registered users.

- If a game was created with only one player, the `game.join_game` endpoint may be utilized at `game/join/[game`s url-safe key]`. `game.join_game` takes one field, `player_two_name`, a *string* of the name from a registered user.

- To cancel a game, the `game.cancel_game` endpoint may be utilized at `game/cancel/[game's url-safe key]` with a `GET` request. This endpoint takes in no fields. Once a game is cancelled, the game and all corresponding entities such as pieces and game history will be deleted.

## Endpoints

### API Endpoint

https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1

- battleship.create_user
  - Request type: `POST`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/user/new`
  - Request fields:
    - `name`: *String*, Required
    - `email`: *String*, Required
  - Response fields:
    - `name`: "[player's name]"
    - `email`: "[Player's e-mail]"


- battleship.create_game
  - Request type: `POST`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/new`
  - Request fields:
    - `player_one_name`: *String* (must be a registered user), Required
    - `player_two_name`: *String* (must be a registered user), Optional
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

- battleship.join_game
  - Request type: `POST`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/join/[game's url-safe key]`
  - Request fields:
    - `player_two_name`: *String* (must be a registered user), Required
  - Response fields:
    - `player_one`: "[player one's name]"
    - `player_two`: "[player two's name]"
    - `player_one_pieces_loaded`: "False"
    - `player_two_pieces_loaded`: "False"
    - `game_started`: "False"
    - `player_turn`: "[Player one's name]"
    - `game_over`: "False"
    - `winner`: "None"
    - `game_key`: "[URL-safe game key]" (This should be stored, as it is the unique identifier needed to make any subsequent requests regarding this game specificially)

- battleship.cancel_game
  - Request Type: `GET`
  - URL: `https://nodar-battle-ship.appspot.com/_ah/api/battle_ship/v1/game/cancel/[game's url-safe key]`
  - Request Fields:
  	- None
  - Response Fields:
    - `message`: "Game deleted"