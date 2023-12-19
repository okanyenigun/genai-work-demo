from django.urls import path
from review.views import MainView, DataMainView, DataAppRecord, DataAppStore, DataExport, NlpMainView, NlpTranslateMain, NlpSentimentView, NlpZeroView

urlpatterns = [
    path('review/main/', MainView.as_view(), name="review_main"),
    path('review/data/', DataMainView.as_view(), name="review_data_main"),
    path('review/data/appRecord/', DataAppRecord.as_view(),
         name="review_data_app_record"),
    path('review/data/appStore/', DataAppStore.as_view(),
         name="review_data_app_store"),
    path('review/data/export/', DataExport.as_view(), name="review_data_export"),

    path('review/nlp/', NlpMainView.as_view(), name="review_nlp_main"),
    path('review/nlp/translate/', NlpTranslateMain.as_view(),
         name="review_nlp_translate"),
    path('review/nlp/sentiment/', NlpSentimentView.as_view(),
         name="review_nlp_sentiment"),
    path('review/nlp/zero/', NlpZeroView.as_view(),
         name="review_nlp_zero"),
]
