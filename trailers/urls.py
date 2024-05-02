from django.urls import path
from trailers import views
app_name = 'trailers'

urlpatterns = [
    path("", views.show_trailers, name="trailers"),
]
