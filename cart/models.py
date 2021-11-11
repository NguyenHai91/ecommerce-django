from django.db import models

from product.models import Product, Variation
from user.models import User

# Create your models here.

class Cart(models.Model):
  cart_id = models.CharField(max_length=200, unique=True)
  date_added = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return self.cart_id


class CartItem(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
  variations = models.ManyToManyField(Variation, blank=True)
  quantity = models.IntegerField()
  is_active = models.BooleanField(default=True)

  def __str__(self):
      return self.product.name

  def sub_total(self):
    return float(self.product.price) * self.quantity
