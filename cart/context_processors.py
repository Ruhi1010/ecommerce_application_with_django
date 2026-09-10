from cart.cart import Cart


def cart(request):
    """Makes `cart` available in every template's context (used for the navbar badge)."""
    return {'cart': Cart(request)}
