import hashlib
import uuid
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, PendingOrder, Food
from django.shortcuts import render, redirect, get_object_or_404
from .models import Food, Order, OrderItem,PendingOrder
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.http import JsonResponse



def home(request):
    foods = Food.objects.all()[:3]
    return render(request, 'home.html', {'foods': foods})


@login_required(login_url='/login/')
def menu(request):
    foods = Food.objects.all()[:9]
    cart = request.session.get('cart', {})  # ← pass cart to template
    return render(request, 'menu.html', {'foods': foods})





# Add to Cart
def get_cart_data(request):
    cart = request.session.get('cart', {})
    return JsonResponse(cart)

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
    return redirect('menu')


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
        # Handle both JSON body (from menu.html) and form POST (from cart.html)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            food_id = str(data.get('food_id'))
            quantity = int(data.get('quantity'))
        else:
            food_id = str(request.POST.get('food_id'))
            quantity = int(request.POST.get('quantity'))

        cart = request.session.get('cart', {})

        if quantity <= 0:
            # Remove item if qty dropped to 0
            cart.pop(food_id, None)
        elif food_id in cart:
            # Update existing item quantity
            cart[food_id]['quantity'] = quantity
        else:
            # New item being added from menu page
            food = Food.objects.get(id=food_id)
            cart[food_id] = {
                'name': food.name,
                'price': float(food.price),
                'quantity': quantity,
                'image': food.image.url
            }

        request.session['cart'] = cart
        request.session.modified = True

        total = sum(item['price'] * item['quantity'] for item in cart.values())
        total_items = sum(item['quantity'] for item in cart.values())

        return JsonResponse({
            'success': True,
            'total': round(total, 2),
            'total_items': total_items
        })

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

def ajax_clear_cart(request):
    if request.method == "POST":
        request.session['cart'] = {}
        request.session.modified = True
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared'
        })
    return JsonResponse({'success': False}, status=400)
# Checkout


@login_required(login_url='/login/')
def checkout(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == "POST":
        name = request.user.get_full_name() or request.user.username
        email = request.user.email
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        # save phone
        request.user.profile.phone = phone
        request.user.profile.save()
        
        

        # save order to DB here...

        request.session['cart'] = {}
        return redirect('order_success')

    return render(request, 'checkout.html', {
        'cart': cart,
        'total': total,
        'user': request.user
    })
# Orders

@login_required(login_url='/login/')
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {
        'orders': orders,
        'active_orders': orders.filter(status='Placed'),
        'past_orders': orders.exclude(status='Placed'),
    })


# @login_required(login_url='/login/')
# def place_order(request):
#     cart = request.session.get('cart', {})

#     if not cart:
#         return redirect('cart')

#     total = 0

#     #  Calculate total correctly
#     for food_id, item in cart.items():
#         food = Food.objects.get(id=food_id)
#         total += food.price * item['quantity']

#     #  Create order
#     order = Order.objects.create(
#         user=request.user,
#         total_price=total,
#         status="Placed"
#     )

#     #  Create order items
#     for food_id, item in cart.items():
#         food = Food.objects.get(id=food_id)
#         OrderItem.objects.create(
#             order=order,
#             food=food,
#             quantity=item['quantity']
#         )

#     #  Clear cart
#     request.session['cart'] = {}

#     return redirect('orders')


@login_required(login_url='/login/')
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    total = 0
    for food_id, item in cart.items():
        food = Food.objects.get(id=food_id)
        total += food.price * item['quantity']

    amount = "{:.2f}".format(float(total))

    name = request.POST.get('name', request.user.username).strip()
    email = request.POST.get('email', request.user.email).strip()
    phone = request.POST.get('phone').strip()
    
    # save in profile
    request.user.profile.phone = phone
    request.user.profile.save()

    txnid = 'TXN' + uuid.uuid4().hex[:10].upper()

    PendingOrder.objects.create(
        user=request.user,
        txnid=txnid,
        total=amount,
        cart_data=cart
    )

    # request.session['cart'] = {}

    hash_string = (
        f"{settings.PAYU_MERCHANT_KEY}|{txnid}|{amount}|Food Order|"
        f"{name}|{email}|||||||||||{settings.PAYU_SALT}"
    )
    generated_hash = hashlib.sha512(
        hash_string.encode('utf-8')
    ).hexdigest()

    payu_data = {
        'key': settings.PAYU_MERCHANT_KEY,
        'txnid': txnid,
        'amount': amount,
        'productinfo': 'Food Order',
        'firstname': name,
        'email': email,
        'phone': phone,
        'surl': request.build_absolute_uri('/payment/success/'),
        'furl': request.build_absolute_uri('/payment/failed/'),
        'hash': generated_hash,
        'payu_url': settings.PAYU_BASE_URL,
    }

    return render(request, 'payment_redirect.html', {'data': payu_data})

@csrf_exempt
def payment_success(request):
    txnid = request.POST.get('txnid') or request.GET.get('txnid', '')
    amount = request.POST.get('amount') or request.GET.get('amount', '')

    try:
        pending = PendingOrder.objects.get(txnid=txnid)

        order = Order.objects.create(
            user=pending.user,          # ✅ user comes from PendingOrder, not session
            txnid=txnid,
            total_price=pending.total,
            status="Placed"
        )

        for food_id, item in pending.cart_data.items():
            food = Food.objects.get(id=food_id)
            OrderItem.objects.create(
                order=order,
                food=food,
                quantity=item['quantity']
            )

        pending.delete()

        # ✅ Clear cart for the correct user's session if they're logged in
        if request.user.is_authenticated:
            request.session['cart'] = {}

    except PendingOrder.DoesNotExist:
        pass
    except Exception as e:
        print("ERROR saving order:", str(e))

    return redirect(f"/payment-success/?txnid={txnid}&amount={amount}")
# @csrf_exempt
# def payment_success(request):
#     txnid = request.POST.get('txnid') or request.GET.get('txnid', '')
#     amount = request.POST.get('amount') or request.GET.get('amount', '')

#     try:
#         pending = PendingOrder.objects.get(txnid=txnid)

#         order = Order.objects.create(
#             user=pending.user,
#             txnid=txnid,   # ✅ ADD THIS
#             total_price=pending.total,
#             status="Placed"
#         )

#         for food_id, item in pending.cart_data.items():
#             food = Food.objects.get(id=food_id)
#             OrderItem.objects.create(
#                 order=order,
#                 food=food,
#                 quantity=item['quantity']
#             )
#         # after order + items created
#         pending.delete()
        
#         # NOW clear cart
#         request.session['cart'] = {}

#     except PendingOrder.DoesNotExist:
#         pass

#     except Exception as e:
#         print("ERROR saving order:", str(e))

#     return redirect(f"/payment-success/?txnid={txnid}&amount={amount}")

def payment_success_page(request):
    txnid = request.GET.get('txnid')
    amount = request.GET.get('amount')

    return render(request, 'payment_success.html', {
        'txnid': txnid,
        'amount': amount
    })
    
@csrf_exempt
def payment_failed(request):
    txnid = request.POST.get('txnid') or request.GET.get('txnid', '')

    PendingOrder.objects.filter(txnid=txnid).delete()

    return render(request, 'payment_failed.html', {
        'error': request.POST.get('error_Message', 'Payment was not completed.')
    })



@login_required(login_url='/login/')
def cancel_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status != "Delivered":
            order.status = "Cancelled"
            order.save()
    return redirect('orders')


# Authentication Views

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






import io
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


@login_required(login_url='/login/')
def download_invoice(request, order_id):
    try:
        order = Order.objects.prefetch_related('items__food').get(
            id=order_id, user=request.user
        )
    except Order.DoesNotExist:
        raise Http404("Order not found")

    if order.status == 'Cancelled':
        return HttpResponse("Invoice not available for cancelled orders.", status=400)

    buffer = io.BytesIO()
    W, H = A4
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)

    styles = getSampleStyleSheet()
    brand_color   = colors.HexColor('#e65c00')
    header_bg     = colors.HexColor('#1a1a2e')
    row_alt       = colors.HexColor('#fff8f3')
    success_green = colors.HexColor('#28a745')

    title_style = ParagraphStyle('T', parent=styles['Normal'], fontSize=26,
        textColor=colors.white, alignment=TA_LEFT, fontName='Helvetica-Bold', leading=30)
    sub_style = ParagraphStyle('S', parent=styles['Normal'], fontSize=9,
        textColor=colors.HexColor('#cccccc'), fontName='Helvetica')
    section_head = ParagraphStyle('SH', parent=styles['Normal'], fontSize=10,
        textColor=brand_color, fontName='Helvetica-Bold', spaceBefore=6)
    normal = ParagraphStyle('N', parent=styles['Normal'], fontSize=9,
        textColor=colors.HexColor('#333333'), fontName='Helvetica', leading=13)
    bold_normal = ParagraphStyle('BN', parent=normal, fontName='Helvetica-Bold')

    story = []

    # --- HEADER ---
    header_table = Table([[
        Paragraph("BCIIT FOODHUB", title_style),
        Paragraph("INVOICE", ParagraphStyle('IR', parent=title_style,
            alignment=TA_RIGHT, fontSize=22, textColor=brand_color)),
    ]], colWidths=[(W-30*mm)*0.6, (W-30*mm)*0.4])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), header_bg),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(header_table)

    sub_table = Table([[
        Paragraph("Campus Canteen, BCIIT Campus, Main Building", sub_style),
        Paragraph("foodhub@bciit.edu.in | +91 98765 43210",
            ParagraphStyle('SR', parent=sub_style, alignment=TA_RIGHT)),
    ]], colWidths=[(W-30*mm)*0.6, (W-30*mm)*0.4])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), header_bg),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 8*mm))

    # --- ORDER META + CUSTOMER INFO ---
    order_no   = f"ORD00{order.id}"
    order_date = order.created_at.strftime("%d %B %Y")
    order_time = order.created_at.strftime("%I:%M %p")
    status_color = {
        'Placed': colors.HexColor('#ffc107'),
        'Delivered': success_green,
        'Cancelled': colors.HexColor('#dc3545'),
        'Pending': colors.HexColor('#17a2b8'),
    }.get(order.status, colors.grey)

    col_w = W - 30*mm
    half  = col_w * 0.5

    def make_info_cell(lines, w):
        t = Table([[p] for p in lines], colWidths=[w])
        t.setStyle(TableStyle([
            ('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
            ('TOPPADDING',(0,0),(-1,-1),1),  ('BOTTOMPADDING',(0,0),(-1,-1),1),
        ]))
        return t

    left_items = [
        Paragraph("ORDER DETAILS", section_head), Spacer(1,2),
        Paragraph(f"<b>Order No:</b>  {order_no}", normal),
        Paragraph(f"<b>Date:</b>  {order_date}", normal),
        Paragraph(f"<b>Time:</b>  {order_time}", normal),
        Paragraph(f"<b>Status:</b>  {order.status}",
            ParagraphStyle('SP', parent=bold_normal, textColor=status_color)),
    ]
    right_items = [
        Paragraph("BILLED TO", section_head), Spacer(1,2),
        Paragraph(f"<b>{request.user.get_full_name() or request.user.username}</b>", normal),
        Paragraph(f"Username:  {request.user.username}", normal),
        Paragraph(f"Email:  {request.user.email or 'N/A'}", normal),
    ]

    meta_table = Table(
        [[make_info_cell(left_items, half-12), make_info_cell(right_items, half-12)]],
        colWidths=[half, half])
    meta_table.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('BOX',(0,0),(-1,-1),0.5, colors.HexColor('#dddddd')),
        ('BACKGROUND',(0,0),(-1,-1), colors.HexColor('#fafafa')),
        ('TOPPADDING',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6*mm))

    # --- ITEMS TABLE ---
    story.append(Paragraph("ORDER ITEMS", section_head))
    story.append(Spacer(1, 2))

    def th(text, align=TA_LEFT):
        return Paragraph(text, ParagraphStyle('TH', parent=bold_normal,
            textColor=colors.white, alignment=align))

    table_data = [[th("#", TA_CENTER), th("Item"), th("Unit Price", TA_RIGHT),
                   th("Qty", TA_CENTER), th("Subtotal", TA_RIGHT)]]

    for idx, item in enumerate(order.items.all(), 1):
        unit_price = item.food.price
        subtotal   = unit_price * item.quantity
        def td(text, align=TA_LEFT):
            return Paragraph(str(text), ParagraphStyle(f'TD{idx}', parent=normal, alignment=align))
        table_data.append([
            td(idx, TA_CENTER), td(item.food.name),
            td(f"Rs. {unit_price}", TA_RIGHT), td(item.quantity, TA_CENTER),
            td(f"Rs. {subtotal}", TA_RIGHT),
        ])

    alt_rows = [('BACKGROUND',(0,i),(-1,i), row_alt if i%2==0 else colors.white)
                for i in range(1, len(table_data))]

    items_table = Table(table_data,
        colWidths=[col_w*0.06, col_w*0.44, col_w*0.18, col_w*0.10, col_w*0.22])
    items_table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), header_bg),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,0),9),
        ('TOPPADDING',(0,0),(-1,0),8), ('BOTTOMPADDING',(0,0),(-1,0),8),
        ('FONTNAME',(0,1),(-1,-1),'Helvetica'), ('FONTSIZE',(0,1),(-1,-1),9),
        ('TOPPADDING',(0,1),(-1,-1),6), ('BOTTOMPADDING',(0,1),(-1,-1),6),
        ('GRID',(0,0),(-1,-1),0.4, colors.HexColor('#dddddd')),
        ('LINEBELOW',(0,0),(-1,0),1, brand_color),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        *alt_rows,
    ]))
    story.append(items_table)
    story.append(Spacer(1, 4*mm))

    # --- TOTALS ---
    tax = round(order.total_price * 0.05)
    grand_total = order.total_price + tax

    def trow(label, value, is_grand=False):
        style = ParagraphStyle('GT', parent=styles['Normal'], fontSize=11 if is_grand else 9,
            fontName='Helvetica-Bold', alignment=TA_RIGHT,
            textColor=colors.white if is_grand else colors.HexColor('#333333'))
        return [Paragraph(label, style), Paragraph(value, style)]

    totals_table = Table([
        # trow("Subtotal:",      f"Rs. {order.total_price}"),
        # trow("Platform Fee:",  "Rs. 0"),
        # trow("Tax (GST 5%):",  f"Rs. {tax}"),
        trow("TOTAL",    f"Rs. {grand_total}", is_grand=True),
    ], colWidths=[col_w*0.72, col_w*0.28])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-2), colors.HexColor('#fafafa')),
        ('BACKGROUND',(0,-1),(-1,-1), brand_color),
        ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('LINEABOVE',(0,-1),(-1,-1),1, colors.white),
        ('BOX',(0,0),(-1,-2),0.5, colors.HexColor('#dddddd')),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 6*mm))

    # --- FOOTER ---
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#dddddd')))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Thank you for ordering from BCIIT FOODHUB!  For support: foodhub@bciit.edu.in",
        ParagraphStyle('F1', parent=styles['Normal'], fontSize=8,
            textColor=colors.grey, alignment=TA_CENTER)))
    story.append(Paragraph(
        f"Invoice generated on {order.created_at.strftime('%d %b %Y')}  |  "
        f"Order #{order_no}  |  This is a computer-generated invoice.",
        ParagraphStyle('F2', parent=styles['Normal'], fontSize=7,
            textColor=colors.HexColor('#aaaaaa'), alignment=TA_CENTER)))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_no}.pdf"'
    return response

  











