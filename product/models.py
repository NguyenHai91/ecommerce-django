
from django.db import models
from django.urls.base import reverse

from category.models import Category


# Create your models here.

class Product(models.Model):
  name = models.CharField(max_length=200)
  slug = models.SlugField(max_length=200, unique=True)
  description = models.TextField(blank=True)
  price = models.CharField(max_length=50)
  images = models.ImageField(upload_to='products')
  in_stock = models.IntegerField(default=0)
  is_available = models.BooleanField(default=True)
  category = models.ForeignKey(Category, on_delete=models.CASCADE)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  

  def get_url(self):
    return reverse('product_detail', args=[self.category.slug, self.slug])

  def __str__(self) -> str:
      return self.name


class VariationManager(models.Manager):
  def colors(self):
    return super(VariationManager, self).filter(variation_category='color', is_active=True)

  def sizes(self):
    return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choice = (
  ('color', 'color'),
  ('size', 'size')
)

class Variation(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  variation_category = models.CharField(max_length=200, choices=variation_category_choice)
  variation_value = models.CharField(max_length=200)
  is_active = models.BooleanField(default=True)
  created_date = models.DateTimeField(auto_now_add=True)

  objects = VariationManager()

  def __str__(self):
    return self.variation_value