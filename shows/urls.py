from django.urls import path
from shows import views
app_name = 'shows'

urlpatterns = [
    path("", views.show_tayangan, name="tayangan"),
    path('<str:id>/', views.tayangan_detail, name='detail'),
    path('<str:id>/episode/<str:sub_judul>/', views.episode_detail, name='episode'),
    path('save_review', views.save_review, name='save_review'),
    path('<str:id>/update_review/', views.update_review, name='update_review'),
    path('save_watching_history', views.save_watching_history, name='save_watching_history'),
]
