from django.shortcuts import render
from products.models import Product


def index(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.all()
    if query:
        products = products.filter(product_name__icontains=query)
    context = {'products': products, 'query': query}
    return render(request, 'home/index.html', context)
