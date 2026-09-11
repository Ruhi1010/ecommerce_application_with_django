from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from products.models import Product
from cart.cart import Cart
from cart.wishlist import Wishlist


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

    if request.POST.get('buy_now'):
        return redirect('checkout')
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


@require_POST
def cart_apply_coupon(request):
    cart = Cart(request)
    code = request.POST.get('code', '')
    if code and cart.apply_coupon(code):
        messages.success(request, f'Coupon "{code}" applied.')
    else:
        messages.warning(request, 'That coupon code is invalid or expired.')
    return redirect('cart_detail')


def cart_remove_coupon(request):
    cart = Cart(request)
    cart.remove_coupon()
    messages.success(request, 'Coupon removed.')
    return redirect('cart_detail')


def wishlist_toggle(request, slug):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, slug=slug)
    saved = wishlist.toggle(product.slug)
    if saved:
        messages.success(request, f'"{product.product_name}" saved to your wishlist.')
    else:
        messages.success(request, f'"{product.product_name}" removed from your wishlist.')

    next_url = request.META.get('HTTP_REFERER')
    return redirect(next_url or 'cart_detail')


def wishlist_detail(request):
    wishlist = Wishlist(request)
    return render(request, 'cart/wishlist.html', {'wishlist': wishlist})
