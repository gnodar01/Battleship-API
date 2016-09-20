#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import BattleshipAPI
from models.ndbModels import Game, User


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send Users with unfinished games reminders, once a day"""
        app_id = app_identity.get_application_id()
        unfinished_games = Game.query(ndb.AND(Game.game_started == True, Game.game_over == False)).fetch()
        print unfinished_games


class SomethingElse(webapp2.RequestHandler):
    def post(self):
        """Memcache thing"""
        pass


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/somethingelse', SomethingElse),
], debug=True)
