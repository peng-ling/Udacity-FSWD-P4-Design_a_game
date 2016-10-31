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




## API endpoints description

### cancel_game

- Purpose: Chancel a running game.
- Argument: urlsafe_game_key
- return value in case of success: 'Game deleted!'
- return value in case game could not be deleted because it's still running: 'Cant delete Game which is not over!'
- In case game was not found a exception is thrown, with message: 'Game not found!'

### create_user

### get_average_attempts_remaining

### get_game

### get_game_hostory

### get_high_scores

### get_user_games

### get_user_rankings

### get_user_scores

### make_move

### new_game


## Explanation of score keeping
