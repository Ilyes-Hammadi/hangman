#Hangman

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Hangman is a simple guessing game. Each game begins with a random generated word,
each word has it's own number of moves, `make_move` endpoint is used to make a move
and it reply with either 'Nice Work' for a correct letter, 'Keep Going' for a bad letter,
'Game Over' if the maximum number of attempts is reached.
Many different Hangman games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists, email must
    be valid will raise a UnauthorizedException.
    
 - **create_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, email
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Min must be less than
    max. Also adds a task to a task queue to update the average moves remaining
    for active games.
     
 - **get_user_games**
    - Path: 'user'
    - Method: GET
    - Parameters: user_name, email
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, letter
    - Returns: GameForm with new game state.
    - Description: Accepts a 'letter' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.

 - **cancel_game**
    - Path: 'game/cancel'
    - Method: PUT
    - Parameters: user_name, email
    - Returns: Message that says that game has been canceled.
    - Description: Cancel the last game played by the user

 - **get_high_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: user_name, email, number_of_results (optional)
    - Returns: ScoreForms.
    - Description: Returns all user Scores in the database ordered by the latest played.
    
 - **get_user_rankings**
    - Path: 'user/rank'
    - Method: GET
    - Parameters: user_name, email
    - Returns: UserForm.
    - Description: Returns user information's with the user rank games won/lost score
    total_played.

 - **get_game_history**
    - Path: 'game/history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: MoveForms
    - Description: Gets all the moves played by the user.

##Models Included:
 - **User**
    - Stores unique user_name ,email and score (default is 0).

 - **Move**
    - Stores the letter played, is_correct boolean variable, message and date time
    of the move.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **UserForm**
    - Representation of User's info's state (name,email,total_played,
     won, lost, score, ranking)

 - **MoveForm**
    - Representation of Move's state (letter_played, is_correct flag, message, date)

 - **MoveForms**
    - Multiple MoveForm container.

 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_allowed,attempts_played,
    attempts_correct, game_over, user_name, mystery_word, word_tried, message, score,
    moves, date).

 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    score, mystery_word).

 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.