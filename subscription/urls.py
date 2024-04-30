from django.urls import path
from subscription.views import *

app_name = "subscription"

urlpatterns = [
    path("my-subscription-package/", get_user_active_package, name="get_user_active_package"),
    path("subscription-packages/", get_all_packages, name="get_all_packages"),
    path("my-subscription-history/", get_transaction_history, name="get_transaction_history"),
    path("", render_subscription_manager, name="render_subscription_manager"),
    path("subscription-packages/<str:package_name>/", get_package_details_by_name, name="get_package_details_by_name"),
    path("subscribe/<str:package_name>/", render_subscription_purchase, name="render_subscription_purchase"),
    path("purchase-subscription/", add_subscription, name="add_subscription"),
    path("uodate-subscription/", update_subscription, name="update_subscription"),
]
