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

- One 5 space ship: `| O | O | O | O | O |`

- One 4 space ship: `| O | O | O | O |`

- Two 3 space ships: `| O | O | O |` + `| O | O | O |`

- One 2 space ship: `| O | O |`

