# Full Stack Web Developer Nanodegree Design a Game API Project

## Requirements to run the Project

### Local Computer

- Python 2.7.10 which you can download [here]https://www.python.org/downloads/.
- Google Python SDK for App Engine which you can download [here]https://cloud.google.com/appengine/docs/python/download.

### Google App Engine

1. Go here: https://console.developers.google.com
2. Select create project.
3. Click edit to view the Project ID field.
4. Choose a unique project id.
5. Give your project a name (doesn't have to be unique).
6. Click create.

## Run the project on your local computer

1. Clone this repository.
2. cd into your local copy.
3. Edit app.yaml, write your project id, which you created ins step 4 in Google App Engine,  here: application: "yourprojectid"
4. Start the Development Web Server by "dev_appserver.py app.yaml" in terminal.
  Some more information on running the App Server you be found [here]https://cloud.google.com/appengine/docs/python/tools/using-local-server
5. You can now access the api explorer by this url: https://apis-explorer.appspot.com/apis-explorer/?base=http://localhost:8080/_ah/api#p/
6. In case you are using Google Chrome, you might need to follow this steps, to run the api explorer:
https://support.google.com/chrome/answer/1342714?hl=en


## Deploy the project to Google App Engine

1. In terminal, make sure you are in the repository root folder.
2. enter: appcfg.py -A "yourprojectid" -V v1 update ./
3. After successfully deployment of the app, you can access it by opening


## How to play the game

First requirement to play hangman is to create a user, this can be done by create_user endpoint.
A user name is mandatory, the email is optional. In case you provide an email you
will receive a remainder email in case you have unfinished games every 24 hours.

To start a new game use the create_game endpoint. You need to provide your user name.
Once the new game is created and the endpoint returns, make sure to remember the
url safe key of the game as it is needed later on.

To make a move submit a guess to the make_move endpoint. The Returned values will
let you know if your guess was wright or wrong, the revealed letters, e.g.
***a**** and the number of guesses left.
Once the number of wrong guesses have reached its limit you will loose the game,
if you guess the whole world with the last possible move or before you will win.

A request of endpoint get_game_history will provide all moves of a game. You need
to provide the url safe key of the game.

To see your scores for each game you finished, you can request the endpoint
get_user_scores. You need to provide your user name.

The see your ranking within the high score of all player request endpoint
get_user_rankings.

To delete a unfinished game request endpoint cancel_game. You need to provide
the url safe game key.


## API endpoints description

### cancel_game

- endpoint path: /game/delete/\<urlsafe_game_key>
- Purpose: Chancel a running game
- HTTP method: DELETE
- Argument: urlsafe_game_key <mandatory>
- return value in case of success: 'Game deleted!'
- return value in case game could not be deleted because it's still running: 'Cant delete Game which is not over!'
- In case game was not found an exception is thrown, with message: 'Game not found!'

### create_user

- endpoint path: /user?email=[email]&user_name=<user_name>
- Purpose: Create a new user
- HTTP method: POST
- Arguments: user_name <mandatory>, email [optional]
- return value in case of success: 'User [user_name] has been success created'.
- In case user already exists an exception is thrown, with message: 'A User with that name already exists!'

### get_average_attempts_remaining

- endpoint path: /games/average_attempts
- Purpose: Returns the average remain attempts over all games.
- HTTP method: GET
- Arguments: None
- return value in case of success: number of average attempts

### get_game

- endpoint path: /game/<urlsafe_game_key>
- Purpose: Returns information on selected game
- HTTP method: GET
- Arguments: urlsafe_game_key <mandatory>
- returned attributes in case of success:
  - message
  - urlsafe_key
  - attempts_remaining
  - game_over
- In case game does not exists an exception is thrown, with message: 'Game not found!'

### get_game_history

- endpoint path: /gamehistory/<urlsafe_game_key>
- Purpose: Returns every move of a specific game
- HTTP method: GET
- Arguments: urlsafe_game_key <mandatory>
- returned attributes in case of success:
  - on item per move with attributes
    - move_no
    - guess
    - matchresult
- In case game does not exists an exception is thrown, with message: 'Game not found!'


### get_high_scores

- endpoint path: /scores?limit=[limit]
- Purpose: Returns the score and some additional information for each game
- HTTP method: GET
- Arguments: limit [optional] , limit how much scores will be returned
- attributes
 - date
 - guesses
 - won
 - user_name

### get_user_games

- endpoint path: /usergames?user_name=<user_name>
- Purpose: Returns all games of a specific user
- Arguments: user_name <mandatory>
- HTTP method: GET
- returned attributes in case of success:
  - on item per game with attributes
    - urlsafe_key
    - user_name
    - attempts_remaining
    - game_over
- returns message 'User does not exist!' in case user is not found


### get_user_rankings
- endpoint path: /ranking
- Purpose: Returns all users with their rankings, ordered by ranking (highest first)
- Arguments: None
- HTTP method: GET
- returned attributes in case of success:
  - on item per game with attributes
    - player_name
    - player_ranking
- In case game does not exists an exception is thrown, with message: 'Ranking not found'


### get_user_scores
- endpoint path: /scores/user/<user_name>
- Purpose: Returns scores of all games for a specific user
- Arguments: user_name <mandatory>
- HTTP method: GET
- returned attributes in case of success:
  - on item per game with attributes
    - date
    - guesses
    - won
    - user_name
  - In case user does not exists an exception is thrown, with message: 'A User with that name does not exist!'


### make_move
- endpoint path: /game/<urlsafe_game_key>
- Purpose: Posts a move with a letter guessed by the user.
- Arguments: urlsafe_game_key <mandatory> and guessed letter <mandatory>
- HTTP method: POST
- returned attributes in case of success:
  - attempts_remaining
  - game_over
  - guessedletters
  - matchresult
  - message"
- In case guess is a not allowed letter or sign message contains related information
- In case guess is empty message contains related information
- In case user tries to make a move for an already ended game message contains related information


### new_game

- endpoint path: /game

- Purpose: Initiates a new game
- Arguments: user_name <mandatory>
- HTTP method: POST
- returned attributes in case of success:
  - attempts_remaining
  - game_over
  - message
  - urlsafe_key
  - user_name
- In case user does not exists an exception is thrown, with message: 'A User with that name does not exist!'


## Explanation of score keeping

The score for each game is the number of remaining guesses after the game is won.
As the secret word can be of any length the maximum number of guesses is computed as the length of the secret
word plus 5.

High score is computed by dividing the the score for each game divided by the number of played games.
Not matter if won or lost.
