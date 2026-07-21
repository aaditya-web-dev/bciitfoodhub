# 🍔 BCIIT FoodHub — Online Food Ordering System

A full-stack food ordering platform built with Django, MySQL, Bootstrap, HTML, CSS. Includes user authentication, a session-based AJAX cart, PayU payment integration, order tracking with PDF invoices, SMS notifications via Twilio, and a separate Admin Dashboard.

## 🚀 Features

### 👤 Customer

- Registration & login
- Browse the food menu
- Add / update / remove items from cart (AJAX, no page reload)
- Checkout with delivery address & phone number
- Pay via PayU (testmode gateway)
- View order history, cancel orders before delivery
- Download a PDF invoice for any completed order
- SMS notifications on order placement / delivery (Twilio)

### 🛠️ Admin

- Dashboard with product count, order count
- Add / edit / delete food items (with image upload)
- View and manage all orders

## 🧑‍💻 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 (Python) |
| Frontend | HTML, Bootstrap, CSS, JavaScript |
| Cart Updates | AJAX (Fetch API) — add/update/remove cart items without page reload |
| Database | MySQL |
| Auth | Django's built-in auth system |
| Payments | PayU (test environment) |
| SMS | Twilio |
| PDF invoices | ReportLab |
| Media storage | Django media files |

## 🗂️ Project Structure

```
Online-Food-Ordering-System-main/
├── manage.py
├── requirements.txt
├── .env.example          # copy to .env and fill in real values
├── food_ordering/        # project settings, root URLconf
└── store/                # main app
    ├── models.py          # Food, Profile, Order, OrderItem, PendingOrder
    ├── views.py           # cart, checkout, PayU flow, invoices, auth
    ├── admin_view.py      # custom /admin-dashboard/ views
    ├── signals.py         # auto-create Profile, order SMS notifications
    ├── utils.py           # Twilio SMS helper
    ├── urls.py / admin_urls.py
    ├── templates/
    └── static/
```

## 🧩 Main Modules Explained

### 🔐 Authentication

- Uses Django's built-in authentication system (`django.contrib.auth`)
- Custom login/register/logout views styled with Bootstrap (`login_view`, `register_view`, `user_logout`)
- A `Profile` model (phone number) is auto-created for every new user via a `post_save` signal


### 🛒 Cart System (AJAX)

- Cart is stored server-side in the Django session (`request.session['cart']`), keyed by food ID
- Add to cart, update quantity, remove item, and clear cart all happen via `fetch()` calls to dedicated endpoints (`ajax_update_cart`, `ajax_remove_item`, `ajax_clear_cart`) with no full page reload
- Cart total and item count are recalculated server-side on every AJAX call and returned as JSON

### 💳 Checkout & Payments

- `checkout` view collects delivery address and phone, saving the phone to the user's `Profile`
- `place_order` recalculates the order total server-side (never trusts client-supplied prices), creates a `PendingOrder`, and redirects to PayU with a SHA-512 signed hash
- `payment_success` verifies PayU's reverse hash and the paid amount against the `PendingOrder` before converting it into a real `Order` — payments that fail verification are rejected
- `payment_failed` cleans up the abandoned `PendingOrder`

### 📦 Order Management

- Orders and their line items are stored in MySQL (`Order`, `OrderItem` models)
- Customers can view active vs. past orders (`orders` view) and cancel an order before it's marked `Delivered`
- `download_invoice` generates a branded PDF invoice on demand using ReportLab

### 🔔 Notifications

- `signals.py` listens for `Order` creation and status changes
- On order placement and delivery, `utils.send_sms` sends the customer an SMS via Twilio (failures are logged, not raised, so a failed text never breaks the order)


## ⚙️ Setup

### Prerequisites

- Python 3.10+
- MySQL server running locally (or reachable)


### 1. Clone & create a virtual environment

```bash
git clone https://github.com/aaditya-web-dev/bciitfoodhub.git
cd bciitfoodhub/Online-Food-Ordering-System-main
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```



### 3. Create the database

```sql
CREATE DATABASE food_db;
```

### 4. Run migrations & create an admin user

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the server

```bash
python manage.py runserver
```

- Storefront: http://127.0.0.1:8000/
- Django admin: http://127.0.0.1:8000/admin/

## 🔒 Security notes

- All secrets (Django key, DB password, PayU keys, Twilio credentials) are loaded from environment variables via `.env` — none are hardcoded in source.
- `DEBUG` defaults to `False` and must be explicitly enabled for local development.
- Set `DJANGO_ALLOWED_HOSTS` to your real domain(s) before deploying.
- PayU payment callbacks are hash-verified server-side before an order is created.


