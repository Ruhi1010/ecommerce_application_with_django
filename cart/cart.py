from decimal import Decimal
from products.models import Product
from cart.models import Coupon

CART_SESSION_KEY = 'cart'
COUPON_SESSION_KEY = 'coupon_id'


class Cart:
    """
    A session-backed shopping cart.
    No database table is needed for the cart items themselves - everything
    lives in request.session, so it works for guests and stays with a user
    across a visit. A coupon, if applied, is looked up from the Coupon model.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def _make_key(self, product, size=None):
        # Same product in a different size is a separate line item.
        return f"{product.uid}_{size or 'default'}"

    def add(self, product, quantity=1, size=None, update_quantity=False):
        key = self._make_key(product, size)

        if size:
            price = product.get_product_price_by_size(size)
        else:
            price = product.price

        if key not in self.cart:
            self.cart[key] = {
                'product_uid': str(product.uid),
                'quantity': 0,
                'size': size,
                'price': str(price),
            }

        if update_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity

        if self.cart[key]['quantity'] <= 0:
            self.remove(key)
        else:
            self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def update(self, key, quantity):
        if key in self.cart:
            if quantity <= 0:
                self.remove(key)
            else:
                self.cart[key]['quantity'] = quantity
                self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.session.pop(COUPON_SESSION_KEY, None)
        self.save()

    def __iter__(self):
        product_uids = [item['product_uid'] for item in self.cart.values()]
        products = Product.objects.filter(uid__in=product_uids)
        products_map = {str(product.uid): product for product in products}

        for key, item in self.cart.items():
            item = item.copy()
            item['key'] = key
            item['product'] = products_map.get(item['product_uid'])
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    # Kept for backwards compatibility with the earlier version of the cart.
    def get_total_price(self):
        return self.get_subtotal()

    # ---------------- coupon handling ----------------

    def apply_coupon(self, code):
        try:
            coupon = Coupon.objects.get(code__iexact=code.strip())
        except Coupon.DoesNotExist:
            return False

        if not coupon.is_valid():
            return False

        self.session[COUPON_SESSION_KEY] = coupon.id
        self.save()
        return True

    def remove_coupon(self):
        self.session.pop(COUPON_SESSION_KEY, None)
        self.save()

    def get_coupon(self):
        coupon_id = self.session.get(COUPON_SESSION_KEY)
        if not coupon_id:
            return None
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            return None
        if not coupon.is_valid():
            return None
        return coupon

    def get_discount_amount(self):
        coupon = self.get_coupon()
        if not coupon:
            return Decimal('0')
        return (self.get_subtotal() * coupon.discount_percent / Decimal('100')).quantize(Decimal('1'))

    def get_total_after_discount(self):
        return self.get_subtotal() - self.get_discount_amount()
