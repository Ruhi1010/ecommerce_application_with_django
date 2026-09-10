from decimal import Decimal
from products.models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    """
    A session-backed shopping cart.
    No database table is needed - everything lives in request.session,
    so it works for guests and stays with a user across a visit.
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

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
