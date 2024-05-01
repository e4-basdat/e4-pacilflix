from django.urls import path
from contributors.views import *

app_name = "contributors"

urlpatterns = [
    path("", render_contributors, name="render_contributors"),
    path("writers/", get_writers, name="get_writers"),
    path("actors/", get_actors, name="get_actors"),
    path("directors/", get_directors, name="get_directors"),
]