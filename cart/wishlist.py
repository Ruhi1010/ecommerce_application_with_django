from products.models import Product

WISHLIST_SESSION_KEY = 'wishlist'


class Wishlist:
    """Session-backed wishlist. Stores a plain list of product slugs."""

    def __init__(self, request):
        self.session = request.session
        wishlist = self.session.get(WISHLIST_SESSION_KEY)
        if wishlist is None:
            wishlist = self.session[WISHLIST_SESSION_KEY] = []
        self.wishlist = wishlist

    def save(self):
        self.session.modified = True

    def toggle(self, slug):
        """Add the product if it's not saved yet, remove it if it is. Returns the new state (True = saved)."""
        if slug in self.wishlist:
            self.wishlist.remove(slug)
            self.save()
            return False
        else:
            self.wishlist.append(slug)
            self.save()
            return True

    def contains(self, slug):
        return slug in self.wishlist

    @property
    def slugs(self):
        return self.wishlist

    def __len__(self):
        return len(self.wishlist)

    def __iter__(self):
        products = Product.objects.filter(slug__in=self.wishlist)
        return iter(products)
