from cart.cart import Cart
from cart.wishlist import Wishlist


def cart(request):
    """Makes `cart` available in every template's context (used for the navbar badge)."""
    return {'cart': Cart(request)}


def wishlist(request):
    """Makes `wishlist` available in every template's context (used for the heart icon state)."""
    return {'wishlist': Wishlist(request)}
