from django.urls import path
from orders.views import checkout, order_success, order_list

urlpatterns = [
    path('', checkout, name='checkout'),
    path('success/<uuid:order_id>/', order_success, name='order_success'),
    path('history/', order_list, name='order_list'),
]
