from django.urls import path
from . import admin_view   # ✅ import admin_view, NOT views

urlpatterns = [
    path('', admin_view.dashboard, name='dashboard'),
    path('products/', admin_view.products, name='admin_products'),
    path('products/add/', admin_view.add_product, name='admin_add_product'),
    path('products/edit/<int:id>/', admin_view.edit_product, name='admin_edit_product'),
    path('products/delete/<int:id>/', admin_view.delete_product, name='admin_delete_product'),
    path('orders/', admin_view.orders, name='admin_orders'),

]
