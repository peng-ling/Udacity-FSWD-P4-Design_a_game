#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import HangmanApi

from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        _user_with_unfinished_games = []
        _app_id = app_identity.get_application_id()
        _users = User.query(User.email != None)
        _games = Game.query(Game.game_over == False).fetch()


        for _g in _games:
            _user_with_unfinished_games.append(_g.user)
        print('JJJJJJJJJJJJJJJJJJJJJJJ')
        print(_user_with_unfinished_games)
       

        for _user in _users:
            if _user.key in _user_with_unfinished_games:
                print('Mail gesendet JJJJJJJJJJJJJJJJJJJJJJJ')
                print(_user.name)
                _subject = 'This is a reminder!'
                _body = 'Hello {}, you have an unfinished hangman game! Go ahead and be a winner!'.format(_user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(_app_id),
                           _user.email,
                           _subject,
                           _body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        HangmanApi._cache_average_attempts()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
