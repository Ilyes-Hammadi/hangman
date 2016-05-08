# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import endpoints
from protorpc import remote, messages


from models import *
from utils import get_by_urlsafe

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
MAKE_MOVE = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2),
    letter=messages.StringField(3, required=True),
    urlsafe_game_key=messages.StringField(4, required=True)
)

USER_SCORES = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2),
    number_of_results=messages.IntegerField(3)
)

USER_RANKING = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2),
    won=messages.IntegerField(3),
    lost=messages.IntegerField(4),
    score=messages.IntegerField(5),
    rank=messages.IntegerField(6)
)

URL_SAFE_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1, required=True),
)


@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Game API"""

    def _get_user(self, request):
        """ Helper method to get the user object """
        email, user_name = self._get_user_info(request)
        user = User.query(User.email == email and User.name == user_name).get()

        if user == None:
            raise endpoints.NotFoundException('User does not exist')
        else:
            return user

    def _get_user_info(self, request):
        """" Helper method to get user info """
        if request.email != None and request.user_name != None:
            user_name = request.user_name
            email = request.email
        else:
            user_name = endpoints.get_current_user().nickname()
            email = endpoints.get_current_user().email()
        return email, user_name

    def _get_last_game_played(self, user):
        """ Get all the last game played """
        return Game.query(Game.user == user.key and Game.game_over == False).get()

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username and email"""

        email, user_name = self._get_user_info(request)

        # check if it's a valid email
        if not '@' in email:
            raise endpoints.UnauthorizedException('This is not a valid email')

        if User.query(User.name == user_name and User.email == email).get():
            raise endpoints.ConflictException('A User with that name or email already exists!')

        user = User(name=user_name, email=email)
        user.put()
        return StringMessage(message='User {} created!'.format(user_name))

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='game',
                      name='create_game',
                      http_method='POST')
    def create_game(self, request):
        """ Create a new Game, Requires a unique username and email """
        user = self._get_user(request)

        games = Game.query(Game.user == user.key and Game.game_over == False).fetch()

        if len(games) == 0:
            Game.new_game(user.key)
            message = 'Game Created'
        else:
            message = 'You have already a running game'

        return StringMessage(message=message)

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """ Get the user games. Requires the user info's """
        user = self._get_user(request)
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')
        games = Game.query(Game.user == user.key)
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(request_message=MAKE_MOVE,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """ Make a move. Requires the user info and the character played. Returns the game state"""

        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        # if there are no running game
        if game == None:
            return GameForm(message="There are no runnig game for this account")
        # if the game it's not over
        if not game.game_over:
            game.make_move(request.letter)
        else:
            return GameForm(message="This game is over")
        return game.to_form()

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """ Cancel a game """
        user = self._get_user(request)
        game = self._get_last_game_played(user)
        if game == None:
            message = 'There no running game for this account'
        else:
            game.end_game(won=False)
            message = 'Game canceled'

        return StringMessage(message=message)

    @endpoints.method(request_message=USER_SCORES,
                      response_message=ScoreForms,
                      path='scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """ Get the user scores, Requires the user info's"""
        user = self._get_user(request)
        if request.number_of_results:
            scores = Score.query(Score.user == user.key).order(Score.score).fetch(limit=request.number_of_results)
        else:
            scores = Score.query(Score.user == user.key).order(Score.score)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=UserForm,
                      path='user/rank',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """ Get the user rank """
        user = self._get_user(request)
        user.get_user_rank()
        return user.to_form()

    @endpoints.method(request_message=URL_SAFE_REQUEST,
                      response_message=MoveForms,
                      path='game/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """ Get the moves history for a game """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        return game.get_move_forms()


api = endpoints.api_server([HangmanApi])
