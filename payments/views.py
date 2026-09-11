import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order

SSLCOMMERZ_SESSION_URL = (
    'https://sandbox.sslcommerz.com/gwprocess/v4/api.php'
    if settings.SSLCOMMERZ_IS_SANDBOX
    else 'https://securepay.sslcommerz.com/gwprocess/v4/api.php'
)


@login_required(login_url='login')
def initiate_payment(request, order_id):
    """
    Builds a payment session with SSLCommerz and redirects the user to their
    hosted payment gateway page (card / bKash / Nagad / Rocket / bank, etc).

    Requires a free sandbox store from https://developer.sslcommerz.com/registration/
    - put the store_id / store_passwd it gives you into settings.py.
    """
    order = get_object_or_404(Order, uid=order_id, user=request.user)

    if not settings.SSLCOMMERZ_STORE_ID or not settings.SSLCOMMERZ_STORE_PASSWORD:
        messages.warning(
            request,
            'Online payment is not configured yet (missing SSLCommerz store credentials). '
            'Choose "Cash on Delivery" instead, or ask your developer to add '
            'SSLCOMMERZ_STORE_ID / SSLCOMMERZ_STORE_PASSWORD in settings.py.'
        )
        return redirect('order_success', order_id=order.uid)

    payload = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': str(order.total),
        'currency': 'BDT',
        'tran_id': str(order.uid),
        'success_url': request.build_absolute_uri('/payments/success/'),
        'fail_url': request.build_absolute_uri('/payments/fail/'),
        'cancel_url': request.build_absolute_uri('/payments/cancel/'),
        'ipn_url': request.build_absolute_uri('/payments/ipn/'),

        'cus_name': order.full_name,
        'cus_email': request.user.email or 'customer@example.com',
        'cus_add1': order.address,
        'cus_city': 'Dhaka',
        'cus_postcode': '1000',
        'cus_country': 'Bangladesh',
        'cus_phone': order.phone,

        'shipping_method': 'NO',
        'num_of_item': order.items.count(),
        'product_name': ', '.join(item.product_name for item in order.items.all()[:5]),
        'product_category': 'General',
        'product_profile': 'general',
    }

    try:
        response = requests.post(SSLCOMMERZ_SESSION_URL, data=payload, timeout=15)
        data = response.json()
    except Exception:
        messages.error(request, 'Could not reach the payment gateway. Please try again.')
        return redirect('checkout')

    if data.get('status') == 'SUCCESS' and data.get('GatewayPageURL'):
        return redirect(data['GatewayPageURL'])

    messages.error(request, 'Payment session could not be created. Please try again.')
    return redirect('checkout')


@csrf_exempt
def payment_success(request):
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    order = get_object_or_404(Order, uid=tran_id)

    # NOTE: for production, validate the transaction with SSLCommerz's
    # "Order Validation API" using val_id before trusting this callback:
    # https://developer.sslcommerz.com/doc/v4/#order-validation-api
    order.payment_status = 'paid'
    order.transaction_id = request.POST.get('val_id') or request.POST.get('bank_tran_id') or ''
    order.save()

    messages.success(request, 'Payment successful! Your order is confirmed.')
    return redirect('order_success', order_id=order.uid)


@csrf_exempt
def payment_fail(request):
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    order = get_object_or_404(Order, uid=tran_id)
    order.payment_status = 'failed'
    order.save()
    messages.error(request, 'Payment failed. You can try again from your order history.')
    return redirect('order_list')


@csrf_exempt
def payment_cancel(request):
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    order = get_object_or_404(Order, uid=tran_id)
    order.payment_status = 'failed'
    order.save()
    messages.warning(request, 'Payment was cancelled.')
    return redirect('order_list')


@csrf_exempt
def payment_ipn(request):
    """
    Server-to-server notification from SSLCommerz. Optional but recommended
    in production as a more reliable source of truth than the browser
    success_url redirect above.
    """
    tran_id = request.POST.get('tran_id')
    if tran_id:
        try:
            order = Order.objects.get(uid=tran_id)
            if request.POST.get('status') == 'VALID':
                order.payment_status = 'paid'
                order.save()
        except Order.DoesNotExist:
            pass
    return render(request, 'payments/ipn_ack.html')
