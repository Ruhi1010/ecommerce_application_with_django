from django.urls import path
from payments.views import (
    initiate_payment, payment_success, payment_fail, payment_cancel, payment_ipn,
)

urlpatterns = [
    path('initiate/<uuid:order_id>/', initiate_payment, name='payment_initiate'),
    path('success/', payment_success, name='payment_success'),
    path('fail/', payment_fail, name='payment_fail'),
    path('cancel/', payment_cancel, name='payment_cancel'),
    path('ipn/', payment_ipn, name='payment_ipn'),
]
