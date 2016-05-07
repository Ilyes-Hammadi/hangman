#!/usr/bin/env python

"""main.py - This file contains handlers that are called by cronjobs."""

import webapp2
from google.appengine.api import mail, app_identity

from models import Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        # """Send a reminder email to each User that have runnig game.
        # Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        games = Game.query(Game.game_over == False).fetch()
        users = []
        for game in games:
            # get the user
            user = game.get_user()
            # check if the user has an email
            if user.email != None:
                users.append(game.get_user())

        subject = 'This is a reminder'
        for user in users:
            body = 'Hello {}, you have a running game come back '.format(user.name)
            mail.send_mail('hangman@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)
], debug=True)
