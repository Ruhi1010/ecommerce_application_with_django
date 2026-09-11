from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from cart.cart import Cart
from orders.models import Order, OrderItem


@login_required(login_url='login')
def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_detail')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')

        if not full_name or not address or not phone:
            messages.warning(request, 'Please fill in your name, address and phone number.')
            return render(request, 'orders/checkout.html', {'cart': cart})

        coupon = cart.get_coupon()
        order = Order.objects.create(
            user=request.user,
            coupon=coupon,
            subtotal=cart.get_subtotal(),
            discount=cart.get_discount_amount(),
            total=cart.get_total_after_discount(),
            full_name=full_name,
            address=address,
            phone=phone,
            payment_method=payment_method,
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].product_name if item['product'] else 'Unknown product',
                size=item['size'],
                price=item['price'],
                quantity=item['quantity'],
            )

        cart.clear()

        if payment_method == 'online':
            return redirect('payment_initiate', order_id=order.uid)

        messages.success(request, 'Your order has been placed!')
        return redirect('order_success', order_id=order.uid)

    return render(request, 'orders/checkout.html', {'cart': cart})


@login_required(login_url='login')
def order_success(request, order_id):
    order = get_object_or_404(Order, uid=order_id, user=request.user)
    return render(request, 'orders/success.html', {'order': order})


@login_required(login_url='login')
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})
