from django.urls import path
from shows import views
app_name = 'shows'

urlpatterns = [
    path("", views.show_tayangan, name="tayangan"),
    path('<str:judul>/', views.tayangan_detail, name='detail'),
    path('<str:judul>/episode/<str:sub_judul>/', views.episode_detail, name='episode'),
    path('save_review', views.save_review, name='save_review'),
    path('<str:judul>/update_review/', views.update_review, name='update_review'),

]
