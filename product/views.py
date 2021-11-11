
from django.core import paginator
from django.shortcuts import get_object_or_404, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from category.models import Category
from product.models import Product
from cart.models import Cart
from cart.views import _cart_id

# Create your views here.

def store(request, category_slug=None):
  category = None
  products = None

  if category_slug != None:
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_available=True)
    products_count = products.count()
  else:
    products = Product.objects.filter(is_available=True)
    products_count = products.count()

  paginator = Paginator(products, 4)
  page = request.GET.get('page')
  paged_products = paginator.get_page(page)
  
  context = {
    'products': paged_products,
    'products_count': products_count,
  }
  return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
  try:
    product = Product.objects.get(slug=product_slug)
    in_cart = Cart.objects.filter(cart_id=_cart_id(request)).exists()
  except Exception as e:
    raise e
  context = {
    'single_product': product,
    'in_cart': in_cart,
  }
  return render(request, 'store/product_detail.html', context)


def search(request):
  if 'keyword' in request.GET:
    keyword = request.GET['keyword']
    if keyword:
      products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
      products_count = products.count()
      print(str(keyword))
      print(str(products))
  context = {
    'products': products,
    'products_count': products_count,
  }

  return render(request, 'store/store.html', context)

def review(request):
  print('hello')
  