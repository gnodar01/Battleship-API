"""Hello World API implemented using Google Cloud Endpoints.

Contains declarations of endpoint, endpoint methods,
as well as the ProtoRPC message class and container required
for endpoint method definition.
"""
import endpoints
from protorpc import messages, message_types, remote

class Hello(messages.Message):
    """String that stores a message."""
    greeting = messages.StringField(1)

@endpoints.api(name='battle_ship', version='v1')
class BattleshipAPI(remote.Service):
    """Battle Ship API v1."""

    @endpoints.method(message_types.VoidMessage, Hello,
      path = "sayHello", http_method='GET', name = "sayHello")
    def say_hello(self, request):
      return Hello(greeting="Hello World")

api = endpoints.api_server([BattleshipAPI])
