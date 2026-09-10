from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from products.models import Product
from cart.cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


@require_POST
def cart_add(request, slug):
    cart = Cart(request)
    product = get_object_or_404(Product, slug=slug)

    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('select_size') or None

    cart.add(product=product, quantity=quantity, size=size)
    messages.success(request, f'"{product.product_name}" was added to your cart.')
    return redirect('cart_detail')


@require_POST
def cart_update(request, key):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(key, quantity)
    return redirect('cart_detail')


def cart_remove(request, key):
    cart = Cart(request)
    cart.remove(key)
    messages.success(request, 'Item removed from cart.')
    return redirect('cart_detail')
