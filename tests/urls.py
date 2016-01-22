from django.conf.urls import include
from django.conf.urls import url


urlpatterns = [
    url(r'^activities', include('activities.urls')),
]
