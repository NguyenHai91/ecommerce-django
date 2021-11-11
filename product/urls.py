
from django.urls import path

from . import views

urlpatterns = [
  path('', views.store, name='store'),
  path('<slug:category_slug>/', views.store, name='products_by_category'),
  path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
  path('<slug:product_slug>/', views.review, name='submit_review'),
  path('search/', views.search, name='search'),
]