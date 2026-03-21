from django.urls import path
from . import views

urlpatterns = [
        path('', views.home, name='home'),
        path('menu/', views.menu, name='menu'),
        path('add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
        path('cart/', views.cart, name='cart'),
        path('update-cart/', views.update_cart, name='update_cart'),
        path('ajax-update-cart/', views.ajax_update_cart, name='ajax_update_cart'),
        path('remove/<int:food_id>/', views.remove_item, name='remove_item'),
        path('ajax-remove-item/', views.ajax_remove_item, name='ajax_remove_item'),

        path('checkout/', views.checkout, name='checkout'),
        path('orders/', views.orders, name='orders'),
        path('place-order/', views.place_order, name='place_order'),
        path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
        

        path('login/', views.login_view, name='login'),
        path('register/', views.register_view, name='register'),
        path('logout/', views.user_logout, name='logout'),

]


    

