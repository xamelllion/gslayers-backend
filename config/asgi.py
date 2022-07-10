import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import rest.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    'http': asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter (
            rest.routing.websocket_urlpatterns
        )
    )
})