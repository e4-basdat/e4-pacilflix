from django.urls import path
from subscription.views import *

app_name = "subscription"

urlpatterns = [
    path("package/", get_user_active_package, name="get_user_active_package"),
    path("packages/", get_all_packages, name="get_all_packages"),
    path("history/", get_transaction_history, name="get_transaction_history"),
]
