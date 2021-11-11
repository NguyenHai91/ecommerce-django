from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
import requests

from product.models import Product, Variation
from .models import Cart, CartItem

# Create your views here.

def _cart_id(request):
  cart = request.session.session_key
  if not cart:
    cart = request.session.create()
  return cart


def add_cart(request, product_id):
  product = Product.objects.get(id=product_id)
  product_variation = []
  if request.method == 'POST':
    for item in request.POST:
      key = item
      value = request.POST[key]
      try:
        variations = Variation.objects.filter(product=product, variation_category__iexact=key, variation_value__iexact=value).first()
        if variations:
          product_variation.append(variations)
      except:
        pass

  try:
    cart = Cart.objects.get(cart_id=_cart_id(request))
  except Cart.DoesNotExist:
    cart = Cart.objects.create(
      cart_id = _cart_id(request)
    )
    cart.save()

  is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart)
  if is_cart_item_exists:
    cart_items = CartItem.objects.filter(product=product, cart=cart)
    existing_variations = []
    id_list = []

    for item in cart_items:
      variations = list(item.variations.all())
      existing_variations.append(variations)
      id_list.append(item.id)

    if product_variation in existing_variations:
      index = existing_variations.index(product_variation)
      item_id = id_list[index]
      item = CartItem.objects.get(id=item_id)
      item.quantity += 1
      item.save()
      return redirect('cart')  
    
  cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
  current_user = request.user
  if current_user and current_user.is_authenticated:
    cart_item.user = request.user

  if len(product_variation) > 0:
    cart_item.variations.clear()
    cart_item.variations.add(*product_variation)
    cart_item.save()
  return redirect('cart')


def remove_cart(request, product_id):
  product = get_object_or_404(Product, id=product_id)
  if request.user & request.user.is_authenticated:
    current_user = request.user
    cart_item = CartItem.objects.filter(product=product, user=current_user).first()
  else:
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.filter(product=product, cart=cart).first()
  if cart_item.quantity > 1:
    cart_item.quantity -= 1
    cart_item.save()
  else:
    cart_item.delete()
  
  return redirect('cart')


def remove_cart_item(request, cart_item_id):
  if request.user.is_authenticated:
    current_user = request.user
    cart_item = CartItem.objects.filter(id=cart_item_id, user=current_user).first()
  else:
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.filter(id=cart_item_id, cart=cart).first()
  cart_item.delete()
  return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
  try:
    cart_items = None
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0

    if request.user.is_authenticated:
      cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_items = CartItem.objects.filter(cart=cart, is_active=True)

    for cart_item in cart_items:
      total += (cart_item.quantity * float(cart_item.product.price))
      quantity += cart_item.quantity
  except ObjectDoesNotExist:
    pass
  
  total = round(total, 2)
  tax = round((2 * total)/100, 2)
  grand_total = round(total + tax, 2)

  context = {
    'cart_items': cart_items,
    'total': total,
    'quantity': quantity,
    'tax': tax,
    'grand_total': grand_total,
  }
  return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request):
  try:
    quantity = 0
    tax = 0
    total = 0
    grand_total = 0
    if request.user.is_authenticated:
      current_user = request.user
      cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    for cart_item in cart_items:
      total += (float(cart_item.product.price) * cart_item.quantity)
      quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    grand_total = round(grand_total, 2)

  except ObjectDoesNotExist:
    pass

  context = {
    'cart_items': cart_items,
    'total': total,
    'quantity': quantity,
    'tax': tax,
    'grand_total': grand_total,
  }
  return render(request, 'store/checkout.html', context)


def place_order(request):
  pass