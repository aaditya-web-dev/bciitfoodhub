from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from store.models import Food, Order

def admin_required(user):
    return user.is_superuser


@user_passes_test(admin_required)
def dashboard(request):
    return render(request, 'admin/dashboard.html', {
        'product_count': Food.objects.count(),
        'order_count': Order.objects.count(),
        'revenue': sum(o.total_price for o in Order.objects.all())
    })

@user_passes_test(admin_required)
def products(request):
    return render(request, 'admin/products.html', {
        'foods': Food.objects.all()
    })


@user_passes_test(admin_required)
def add_product(request):
    if request.method == 'POST':
        Food.objects.create(
            name=request.POST['name'],
            price=request.POST['price'],
            image=request.FILES['image']
        )
        return redirect('admin_products')
    return render(request, 'admin/add_product.html')


@user_passes_test(admin_required)
def edit_product(request, id):
    food = get_object_or_404(Food, id=id)
    if request.method == 'POST':
        food.name = request.POST['name']
        food.price = request.POST['price']
        if 'image' in request.FILES:
            food.image = request.FILES['image']
        food.save()
        return redirect('admin_products')
    return render(request, 'admin/edit_product.html', {'food': food})


@user_passes_test(admin_required)
def delete_product(request, id):
    Food.objects.filter(id=id).delete()
    return redirect('admin_products')


@user_passes_test(admin_required)
def orders(request):
    return render(request, 'admin/orders.html', {
        'orders': Order.objects.all()
    })

