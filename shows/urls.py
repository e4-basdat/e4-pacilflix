from django.urls import path
from shows import views
app_name = 'shows'

urlpatterns = [
    path("", views.show_tayangan, name="tayangan"),
    path('<str:judul>/', views.tayangan_detail, name='detail'),
]
