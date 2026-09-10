from django.urls import path
from cart.views import cart_detail, cart_add, cart_update, cart_remove

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/<slug>/', cart_add, name='cart_add'),
    path('update/<key>/', cart_update, name='cart_update'),
    path('remove/<key>/', cart_remove, name='cart_remove'),
]
