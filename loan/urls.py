from django.urls import path
from loan.views import MainView, ajax_message_handler, loading_view

urlpatterns = [
    path('loan/main/', MainView.as_view(), name="loan_main"),
    path('ajax/message_handler/', ajax_message_handler,
         name='ajax_message_handler'),
    path('loan/main/loading/', loading_view, name="loan_loading")
]
