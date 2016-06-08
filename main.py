#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from api import 

from models import 


class Something(webapp2.RequestHandler):
    def get(self):
        """Some cronjob thing"""
        pass


class SomethingElse(webapp2.RequestHandler):
    def post(self):
        """Memcache thing"""
        pass


app = webapp2.WSGIApplication([
    ('/crons/something', Something),
    ('/tasks/somethingelse', SomethingElse),
], debug=True)
