from django.urls import path
from monitor.consumers import TwoConsumer

ws_urlpatterns = [
    path('ws/two_url/', TwoConsumer.as_asgi())
]
