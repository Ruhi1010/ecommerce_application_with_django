from django.urls import path
from cart.views import (
    cart_detail, cart_add, cart_update, cart_remove,
    cart_apply_coupon, cart_remove_coupon,
    wishlist_toggle, wishlist_detail,
)

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/<slug>/', cart_add, name='cart_add'),
    path('update/<key>/', cart_update, name='cart_update'),
    path('remove/<key>/', cart_remove, name='cart_remove'),
    path('coupon/apply/', cart_apply_coupon, name='cart_apply_coupon'),
    path('coupon/remove/', cart_remove_coupon, name='cart_remove_coupon'),

    # wishlist lives under /cart/wishlist/... so it can share this app's urls.py
    path('wishlist/', wishlist_detail, name='wishlist_detail'),
    path('wishlist/toggle/<slug>/', wishlist_toggle, name='wishlist_toggle'),
]
