from django.urls import path
from subscription.views import *

app_name = "subscription"

urlpatterns = [
    path("active-subscription/", get_active_subscription, name="get_active_subscription"),
    path("subscription-details/<str:package_name>/", get_subscription_details_by_name, name="get_subscription_details_by_name"),
    path("subscription-details/", get_all_subscription_details, name="get_all_subscription_details"),
    path("transactions/", get_transaction_history, name="get_transaction_history"),
    path("is-eligible-to-subscribe/", get_subscription_eligibilty, name="get_subscription_eligibilty"),
    path("purchase-subscription/", purchase_subscription, name="purchase_subscription"),
    path("", render_subscription_details, name="render_subscription_details"),
    path("subscribe/<str:package_name>/", render_subscription_purchase, name="render_subscription_purchase"),
]
