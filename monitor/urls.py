from django.urls import path
from monitor.views import two, BuildView, ajax_message_handler_monitor, save_chart_image

urlpatterns = [
    path('two/', two, name="real"),
    path('two/build/', BuildView.as_view(), name="monitor_build"),
    path('ajax/message_handler_monitor/', ajax_message_handler_monitor,
         name='ajax_message_handler_monitor'),
    path('two/ajax/saveimage/', save_chart_image, name='save_chart_image'),
]
