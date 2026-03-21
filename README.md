## 🍔 Online Food Ordering System (Django)

A full-stack Online Food Ordering System built using Django, Bootstrap, CSS, JavaScript, and MySQL, featuring user authentication, cart management, checkout, order tracking, and a separate Admin Dashboard for managing products and orders.

 ## 🚀 Features
 👤 User Features

User Registration & Login,
View Food Menu,
Add / Remove Items from Cart,
Update Quantity,
Checkout with Address & Phone,
Place Orders,
Cancel Orders (before delivery).

 ## 🛠️ Admin Features (Separate Dashboard)

Secure Admin Login,
Add / Edit / Delete Products,
View All Orders,
Order Status Management,
Dashboard Analytics (Total Orders, Products).

## 🎨 UI & Tech

Responsive UI with Bootstrap,
Custom styling using CSS,
Dynamic cart using JavaScript,
Media handling for food images.

## 🧑‍💻 Tech Stack
Layer	Technology,
Backend	Django (Python),
Frontend	HTML, Bootstrap, CSS, JavaScript,
Database	MySQL,
Authentication	Django Auth,
Media Storage	Django Media Files.

## 📂 Project File Structure

food_project/
│
├── food_ordering/                # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── store/                        # Main application
│   ├── migrations/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── images/
│   │       └── hero-food.jpg
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── menu.html
│   │   ├── cart.html
│   │   ├── checkout.html
│   │   ├── orders.html
│   │   ├── login.html
│   │   ├── register.html
│   │
│   │   └── admin/               # Separate Admin Dashboard
│   │       ├── dashboard.html
│   │       ├── products.html
│   │       ├── add_product.html
│   │       ├── edit_product.html
│   │       └── orders.html
│   │
│   ├── admin.py
│   ├── admin_urls.py            # Custom admin routing
│   ├── admin_views.py           # Admin logic
│   ├── apps.py
│   ├── models.py
│   ├── views.py                 # User views
│   ├── urls.py
│   └── tests.py
│
├── media/
│   └── foods/
│       ├── burger.jpg
│       ├── pasta.jpg
│       ├── pizza.jpg
│       └── sandwich.jpg
│
├── manage.py
└── requirements.txt

## 🗂️ Main Modules Explained
 🔐 Authentication

Uses Django’s built-in authentication system,
Login & Register pages styled with Bootstrap,
Session-based cart support.

## 🛒 Cart System

Add items to cart,
Update quantity,
Remove items,
Dynamic total calculation.

## 📦 Order Management

Orders stored in MySQL,
Order items linked to products,
User can view order history,
Cancel order option.

