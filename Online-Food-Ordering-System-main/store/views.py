from django.shortcuts import render, redirect, get_object_or_404
from .models import Food, Order, OrderItem
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse



def home(request):
    foods = Food.objects.all()[:3]
    return render(request, 'home.html', {'foods': foods})


@login_required(login_url='/login/')
def menu(request):
    foods = Food.objects.all()[:9]
    return render(request, 'menu.html', {'foods': foods})




# Add to Cart
def add_to_cart(request, food_id):
    cart = request.session.get('cart', {})
    food = Food.objects.get(id=food_id)

    if str(food_id) in cart:
        cart[str(food_id)]['quantity'] += 1
    else:
        cart[str(food_id)] = {
            'name': food.name,
            'price': food.price,
            'quantity': 1,
            'image': food.image.url   # ✅ add this
        }

    request.session['cart'] = cart
    return redirect('cart')


# View Cart
def cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    return render(request, 'cart.html', {
        'cart': cart,
        'total': total
    })


# Update Cart
def update_cart(request):
    if request.method == "POST":
        cart = request.session.get('cart', {})

        for food_id, qty in request.POST.items():
            if food_id in cart:
                cart[food_id]['quantity'] = int(qty)

        request.session['cart'] = cart
    return redirect('cart')

def ajax_update_cart(request):
    if request.method == "POST":
        food_id = request.POST.get('food_id')
        quantity = int(request.POST.get('quantity'))

        cart = request.session.get('cart', {})

        if food_id in cart:
            cart[food_id]['quantity'] = quantity

        request.session['cart'] = cart

        total = sum(
            item['price'] * item['quantity']
            for item in cart.values()
        )

        return JsonResponse({'total': total})
    return JsonResponse({'error': 'Invalid request'}, status=400) 

# Remove item

def remove_item(request, food_id):
    cart = request.session.get('cart', {})

    if str(food_id) in cart:
        del cart[str(food_id)]

    request.session['cart'] = cart
    return redirect('cart')

def ajax_remove_item(request):
    food_id = request.POST.get('food_id')
    cart = request.session.get('cart', {})

    if food_id in cart:
        del cart[food_id]

    request.session['cart'] = cart

    total = sum(
        item['price'] * item['quantity']
        for item in cart.values()
    )

    return JsonResponse({'total': total})


# Checkout


@login_required(login_url='/login/')
def checkout(request):
    cart = request.session.get('cart', {})

    # calculate total
    total = sum(
        item['price'] * item['quantity']
        for item in cart.values()
    )

    if request.method == "POST":
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # after order placed → clear cart
        request.session['cart'] = {}

        return redirect('order_success')  # optional

    return render(request, 'checkout.html', {
        'cart': cart,
        'total': total
    })
# Orders


@login_required(login_url='/login/')
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'orders.html', {'orders': orders})


@login_required(login_url='/login/')
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    total = 0

    #  Calculate total correctly
    for food_id, item in cart.items():
        food = Food.objects.get(id=food_id)
        total += food.price * item['quantity']

    #  Create order
    order = Order.objects.create(
        user=request.user,
        total_price=total,
        status="Placed"
    )

    #  Create order items
    for food_id, item in cart.items():
        food = Food.objects.get(id=food_id)
        OrderItem.objects.create(
            order=order,
            food=food,
            quantity=item['quantity']
        )

    #  Clear cart
    request.session['cart'] = {}

    return redirect('orders')


@login_required(login_url='/login/')
def cancel_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status != "Delivered":
            order.status = "Cancelled"
            order.save()
    return redirect('orders')


# Authentication Views

# def login_view(request):
#     if request.method == 'POST':
#         user = authenticate(username=request.POST['username'], password=request.POST['password'])
#         if user:
#             login(request, user)
#             return redirect('home')
#         return render(request, 'login.html')

#     return render(request, 'login.html')
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔐 Admin user
            if user.is_staff or user.is_superuser:
                return redirect('/admin/')

            # 🍔 Normal food-ordering user
            return redirect('home')

        return render(request, 'login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'login.html')



def user_logout(request):
    logout(request)
    return redirect('login')


from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'register.html')




  











