#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import BattleshipAPI
from models.ndbModels import Game, User
from utils import get_by_urlsafe


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send Users with unfinished games reminders, once a day,
        if it's their turn to play"""
        app_id = app_identity.get_application_id()
        unfinished_games = Game.query(ndb.AND(
                                     Game.game_started == True,
                                     Game.game_over == False)).fetch()
        users = {}
        for game in unfinished_games:
            user_id = game.player_turn.id()
            user = User.get_by_id(user_id)
            if user_id in users:
                users[user_id]['num_games_in_progress'] += 1
            else:
                users[user_id] = {'num_games_in_progress': 1,
                                  'email': user.email,
                                  'name': user.name}
        for u_id in users:
            subject = 'This is a reminder!'
            body = '''Hello {}, you currently have {} Battle Ship
                   games in progress!'''.format(
                                        users[u_id]['name'],
                                        users[u_id]['num_games_in_progress'])
            # The arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           users[u_id]['email'],
                           subject,
                           body) 

class UpdateAvgMovesPerGame(webapp2.RequestHandler):
    def post(self):
        """Memcache thing"""
        BattleshipAPI._cache_average_moves()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_moves', UpdateAvgMovesPerGame),
], debug=True)

