from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('', include('review.urls')),
    path('', include('loan.urls')),
    path('', include('monitor.urls')),
]
