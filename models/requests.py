"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages, message_types


class UserRequest(messages.Message):
    user_name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)

