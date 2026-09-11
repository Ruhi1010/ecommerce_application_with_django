# My Django E-Commerce Project — Documentation

This is a complete e-commerce website I built with Django. It supports product
browsing & search, categories with color/size variations, email-verified user accounts,
a session/guest shopping cart, a wishlist, coupon codes, checkout with Cash-on-Delivery
or online payment (I integrated the SSLCommerz gateway), and an order history/admin panel.

I'm writing this documentation the way I'd want to read it myself if I came back to this
project in six months and forgot how everything fits together — so it's part build log,
part reference guide.

---

## Table of Contents

1. [Why I Chose This Stack](#1-why-i-chose-this-stack)
2. [How I Structured the Project](#2-how-i-structured-the-project)
3. [What You Need Before We Start](#3-what-you-need-before-we-start)
4. [Step-by-Step: How I Built & Run This Project](#4-step-by-step-how-i-built--run-this-project)
5. [My Project Structure](#5-my-project-structure)
6. [My App-by-App Reference](#6-my-app-by-app-reference)
7. [My Data Models](#7-my-data-models)
8. [My URL Map](#8-my-url-map)
9. [How I Configured Settings & Environment](#9-how-i-configured-settings--environment)
10. [How I Use the Admin Panel](#10-how-i-use-the-admin-panel)
11. [The Workflows I Designed](#11-the-workflows-i-designed)
12. [Problems I Ran Into (and How I Fixed Them)](#12-problems-i-ran-into-and-how-i-fixed-them)
13. [How I Plan to Deploy This](#13-how-i-plan-to-deploy-this)
14. [What I'd Still Like to Improve](#14-what-id-still-like-to-improve)

---

## 1. Why I Chose This Stack

| Layer | Technology | Why I picked it |
|---|---|---|
| Language | Python 3 | Readable, and it's what Django needs |
| Framework | Django 5.x (`Django>=5.0`) | Batteries-included — auth, admin, ORM all out of the box, so I didn't have to build those myself |
| Database | SQLite (default, file-based) | Zero setup while I was building and testing locally |
| Images | Pillow | Required by Django's `ImageField`, which I use for products, categories, and profile photos |
| HTTP client | `requests` | I use this to talk to the SSLCommerz payment API |
| Templating | Django Template Language | Server-rendered HTML, kept things simple since I didn't need a separate frontend framework |
| Payment gateway | SSLCommerz (sandbox/live) | Popular in my target market (Bangladesh) — supports cards and mobile banking. Optional: Cash on Delivery works without it |
| Auth | Django's built-in `django.contrib.auth` | Extended with my own `Profile` model so I could add email verification |

---

## 2. How I Structured the Project

I followed Django's standard "project + apps" layout, which I like because it keeps
each concern in its own box. My project package is **`ecomm`** (settings, root URLs,
WSGI), and I split the actual functionality into **6 focused apps**:

```
ecomm (project config)
 ├── home        → landing page + product search
 ├── products    → Category / Product / variations / product images
 ├── accounts    → registration, login/logout, email verification
 ├── cart        → session-based cart, coupons, wishlist
 ├── orders      → checkout, order creation, order history
 ├── payments    → SSLCommerz payment gateway integration
 └── base        → shared abstract model (UUID pk + timestamps) + email helper
```

**A few design decisions I made, and why:**

- **I kept the cart and wishlist out of the database entirely.** They live in
  `request.session` (see `cart/cart.py` and `cart/wishlist.py`). I did this so guest
  users get a working cart automatically without needing an account — the trade-off is
  it's lost if someone clears cookies or switches devices, which I'm fine with for now.
- **I made every "real" model inherit from `base.models.BaseModel`**, which gives me a
  UUID primary key (`uid`) plus `created_at`/`updated_at` timestamps for free, so I
  never have to redeclare them on each model.
- **I snapshot the product name and price onto `OrderItem`** at the time of purchase, so
  if I ever rename, reprice, or delete a product later, past orders still show what the
  customer actually paid.
- **I made payment pluggable**: `payment_method` is either `cod` (Cash on Delivery,
  works with zero configuration — my default) or `online` (redirects to SSLCommerz's
  hosted payment page once I've added my store credentials).

---

## 3. What You Need Before We Start

Here's what I made sure I had installed before touching the code:

- **Python 3.10+** (Django 5 needs 3.10 or newer) — [python.org](https://www.python.org/downloads/)
- **pip** (comes with Python)
- **Git** (optional — only needed if I want to version/clone the project)
- A code editor (I used VS Code)
- (Optional, for real emails) A Gmail account with an **App Password**, or any SMTP
  credentials
- (Optional, for online payments) A free **SSLCommerz sandbox account**

I checked my Python version with:

```bash
python --version
```

---

## 4. Step-by-Step: How I Built & Run This Project

### Step 1 — Get the project files

If you grabbed this as a ZIP, extract it. If I'm cloning it from my own repo:

```bash
git clone <my-repository-url>
cd ecommerce_application_with_django
```

### Step 2 — Create and activate a virtual environment

I always isolate a project's packages from the rest of my system with a venv.

**Windows (PowerShell / cmd):**
```bash
python -m venv ecomm_env
ecomm_env\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv ecomm_env
source ecomm_env/bin/activate
```

I know it worked when my terminal prompt shows `(ecomm_env)` in front of it.

> Note: my project folder already has an `ecomm_env/` in it from my own machine. I don't
> reuse that one on a new machine — venvs are tied to the exact Python install that
> created them, so I delete it and make a fresh one with the commands above.

### Step 3 — Install my dependencies

```bash
pip install -r requirements.txt
```

This installs everything I rely on:
- `Django>=5.0`
- `Pillow` (for my `ImageField`s — product, category, profile images)
- `requests` (for my SSLCommerz payment calls)

### Step 4 — Configure my environment-sensitive settings

I open `ecomm/settings.py` and check the block near the bottom:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
# EMAIL_HOST_USER = 'email address of host user'
# EMAIL_HOST_PASSWORD = 'google app password'

SSLCOMMERZ_STORE_ID = ''
SSLCOMMERZ_STORE_PASSWORD = ''
SSLCOMMERZ_IS_SANDBOX = True
```

I give myself two options for email (used to send the account-activation link on
signup):

- **For quick local testing (what I usually do):** I switch the backend so emails
  print straight to my terminal instead of actually sending:
  ```python
  EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
  ```
- **For real email delivery:** I uncomment `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`
  and fill in my address plus a Gmail **App Password** (not my regular password — I
  generate one under Google Account → Security → App Passwords).

Online payments are optional for me — I can leave `SSLCOMMERZ_STORE_ID`/
`SSLCOMMERZ_STORE_PASSWORD` blank and the site just nudges customers toward "Cash on
Delivery" instead. When I'm ready to enable online payments, I register for free at
https://developer.sslcommerz.com/registration/ and paste in the sandbox `store_id` /
`store_passwd` I get.

> **Security reminder to myself:** once this is more than a local test, I need to move
> `SECRET_KEY`, email credentials, and payment credentials out of `settings.py` and into
> environment variables (see [Section 9](#9-how-i-configured-settings--environment)).

### Step 5 — Apply my database migrations

This creates `db.sqlite3` and all the tables for every app I wrote:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6 — Create my admin (superuser) account

```bash
python manage.py createsuperuser
```

I follow the prompts for username, email, and password.

> The `post_save` signal I wrote on `User` (in `accounts/models.py`) automatically
> creates a matching `Profile` for every new user, including superusers I create this
> way — but it's **not** automatically email-verified. If I can't log in to my own
> storefront with this account, I verify it manually via the admin panel (see
> [Section 10](#10-how-i-use-the-admin-panel)) or flip `is_email_verified=True` on its
> `Profile`.

### Step 7 — Collect static files (optional while I'm developing)

I only need this for production, but it doesn't hurt to run locally:

```bash
python manage.py collectstatic
```

### Step 8 — Run my development server

```bash
python manage.py runserver
```

Then I visit:
- My storefront: **http://127.0.0.1:8000/**
- My admin panel: **http://127.0.0.1:8000/admin/**

### Step 9 — Add some real data

I log in to `/admin/` with my superuser and create things in this order (each one
depends on the last):

1. **Categories** (`Products → Categories`) — name + image.
2. **Color Variations** / **Size Variations** (optional, only if a product needs them) —
   each can carry its own price add-on.
3. **Products** (`Products → Products`) — name, category, base price, description,
   I attach color/size variations, and add one or more **Product Images** inline.
4. **Coupons** (`Cart → Coupons`) — optional, e.g. code `SAVE10`, 10% off.

Then I go back to my storefront, register a test account, verify its email (console
output or real inbox), log in, add products to my cart, and walk through checkout
myself to make sure everything works end to end.

### Step 10 — Stop the server / step out of the environment

- I stop the server with `Ctrl + C`.
- I leave the virtual environment with `deactivate`.

---

## 5. My Project Structure

```
ecommerce_application_with_django/
├── manage.py                  # Django's command-line entry point
├── requirements.txt           # my Python dependencies
├── db.sqlite3                 # my SQLite database (created after migrate)
├── ecomm/                     # my project package
│   ├── settings.py            # all my configuration (apps, DB, email, payment keys...)
│   ├── urls.py                # root URL router — includes every app's urls.py
│   ├── wsgi.py / asgi.py      # deployment entry points
├── base/                      # shared code, no own URLs/views
│   ├── models.py              # BaseModel: uid (UUID pk), created_at, updated_at
│   └── emails.py              # send_account_activation_email()
├── home/                      # my landing page
│   ├── views.py                # index(): lists/searches products
│   └── urls.py
├── products/                  # my catalog
│   ├── models.py               # Category, Product, ColorVariation, SizeVariation, ProductImage
│   ├── views.py                 # get_product(): product detail page
│   └── urls.py
├── accounts/                  # my auth system
│   ├── models.py                # Profile (email verification, avatar)
│   ├── views.py                  # login_page, register_page, activate_email, logout_user
│   └── urls.py
├── cart/                      # my session cart + wishlist + coupons
│   ├── cart.py                  # Cart class (session-backed)
│   ├── wishlist.py               # Wishlist class (session-backed)
│   ├── models.py                  # Coupon
│   ├── context_processors.py       # injects `cart`/`wishlist` into every template
│   ├── views.py
│   └── urls.py
├── orders/                    # my checkout & order history
│   ├── models.py                # Order, OrderItem
│   ├── views.py                  # checkout, order_success, order_list
│   └── urls.py
├── payments/                  # my SSLCommerz integration
│   ├── views.py                  # initiate_payment, payment_success/fail/cancel/ipn
│   └── urls.py
├── templates/                 # all my HTML templates, grouped by app
│   ├── base/                    # base.html layout + alert.html (messages)
│   ├── home/, product/, accounts/, cart/, orders/, payments/
├── public/static/              # uploaded media (product/category/profile images) + static source
├── html/                       # the original static HTML/CSS theme I adapted this from
└── staticfiles/                # output of collectstatic (generated, production only)
```

---

## 6. My App-by-App Reference

### 6.1 `base`

Not a "real" Django app with routes — just shared infrastructure I built so I wouldn't
repeat myself:

- **`BaseModel`** (abstract): gives every model I write a UUID primary key (`uid`) and
  `created_at` / `updated_at` timestamps for free. Any model that needs these just
  inherits from it: `class Product(BaseModel): ...`
- **`send_account_activation_email(email, email_token)`**: builds and sends my "verify
  your account" email containing a link to `/accounts/activate/<email_token>/`.

### 6.2 `home`

- **`index(request)`** — renders my landing page (`home/index.html`). I read an
  optional `?q=` query string and filter `Product` by
  `product_name__icontains=query`, so the same view powers both my homepage and my
  search bar — I didn't want to write two separate views for that.
- URL: `/` → `index`

### 6.3 `products`

My catalog data and product detail page.

- **`get_product(request, slug)`** — looks up a `Product` by its slug, renders
  `product/product.html`. If I pass a `?size=` query parameter, I recalculate the price
  for that size using `Product.get_product_price_by_size()`.
- URL: `/products/<slug>/` → `get_product`

### 6.4 `accounts`

My registration, login, logout, and email verification flow — I kept these as
function-based views rather than reaching for Django REST framework or class-based auth
views, since I wanted full control over the logic.

- **`register_page`** — creates a `User` (I use email as the username), sets the
  password with `set_password()` (properly hashed), and relies on the `post_save`
  signal in `accounts/models.py` to auto-create a `Profile` and send the activation
  email.
- **`login_page`** — looks up the user by username (email), blocks login if
  `profile.is_email_verified` is `False`, then authenticates and logs in. If I leave
  the "remember me" checkbox (`remember`) unchecked, I set the session to expire when
  the browser closes (`set_expiry(0)`). I also support a `?next=` redirect target.
- **`activate_email`** — looks up a `Profile` by its `email_token` (a UUID I generate at
  signup), flips `is_email_verified` to `True`.
- **`logout_user`** — logs the user out and redirects home.

URLs: `/accounts/register/`, `/accounts/login/`, `/accounts/activate/<email_token>/`,
`/accounts/logout/`

### 6.5 `cart`

Everything I wrote around the shopping cart, wishlist, and coupons — all
**session-based**, with no database rows for cart contents.

- **`Cart`** class (`cart/cart.py`): I add/update/remove line items, keyed by
  `"<product_uid>_<size-or-default>"` so the same product in two different sizes counts
  as two separate line items. I also handle coupon application here (`apply_coupon`,
  `remove_coupon`, `get_discount_amount`, `get_total_after_discount`).
- **`Wishlist`** class (`cart/wishlist.py`): a simple session list of product slugs with
  a `toggle()` method to add/remove.
- **`Coupon`** model: `code`, `discount_percent`, `active`, optional `valid_from`/
  `valid_to` window, with an `is_valid()` helper I check before applying it.
- **Context processor** (`cart/context_processors.py`): I inject `cart` and `wishlist`
  into **every** template's context automatically (registered in
  `settings.py → TEMPLATES → OPTIONS → context_processors`) — that's how my cart icon
  count shows up in the header on every page without me passing it in manually from
  every view.

URLs: `/cart/`, `/cart/add/<slug>/`, `/cart/update/<key>/`, `/cart/remove/<key>/`,
`/cart/coupon/apply/`, `/cart/coupon/remove/`, `/cart/wishlist/`,
`/cart/wishlist/toggle/<slug>/`

### 6.6 `orders`

- **`checkout`** *(login required)* — I block empty carts, validate shipping fields on
  `POST`, create an `Order` (snapshotting subtotal/discount/total and the chosen
  coupon), create one `OrderItem` per cart line (snapshotting product name/price), then
  clear the cart. From there I either redirect to `payment_initiate` (online) or
  straight to `order_success` (Cash on Delivery).
- **`order_success`** *(login required)* — the order confirmation page; I 404 if the
  order doesn't belong to the logged-in user.
- **`order_list`** *(login required)* — a user's order history, newest first.

URLs: `/checkout/`, `/checkout/success/<uuid:order_id>/`, `/checkout/history/`

### 6.7 `payments`

I wrapped the **SSLCommerz** payment gateway here (popular in Bangladesh — supports
cards, mobile banking like bKash/Nagad/Rocket, and net banking).

- **`initiate_payment`** *(login required)* — if I haven't configured store credentials
  yet, I fall back gracefully with a warning message instead of crashing. Otherwise, I
  post an order payload to SSLCommerz's session API and redirect the browser to the
  `GatewayPageURL` it returns.
- **`payment_success` / `payment_fail` / `payment_cancel`** — the browser-redirect
  callback endpoints SSLCommerz sends the user back to; I use them to update
  `Order.payment_status`. I marked these `@csrf_exempt` because the gateway POSTs to
  these from an external domain. ⚠️ See
  [Section 14](#14-what-id-still-like-to-improve) — I still need to validate the
  success callback server-side before trusting it in production.
- **`payment_ipn`** — a server-to-server "Instant Payment Notification" webhook,
  independent of the user's browser — I treat this as the more reliable source of truth
  for whether a payment actually cleared.

URLs: `/payments/initiate/<uuid:order_id>/`, `/payments/success/`, `/payments/fail/`,
`/payments/cancel/`, `/payments/ipn/`

---

## 7. My Data Models

| Model | App | Key fields | Notes |
|---|---|---|---|
| `BaseModel` (abstract) | base | `uid` (UUID, PK), `created_at`, `updated_at` | I inherit this in most models below |
| `Profile` | accounts | `user` (1-to-1), `is_email_verified`, `email_token`, `profile_image` | Auto-created via my signal on `User` creation |
| `Category` | products | `category_name`, `slug` (auto), `category_image` | I auto-slugify the name in `save()` |
| `ColorVariation` | products | `color_name`, `price` | Price is an add-on to my base product price |
| `SizeVariation` | products | `size_name`, `price` | Price is an add-on to my base product price |
| `Product` | products | `product_name`, `slug` (auto), `category` (FK), `price`, `product_description`, `color_variation` (M2M), `size_variation` (M2M) | `get_product_price_by_size(size)` adds the size's price delta |
| `ProductImage` | products | `product` (FK), `image` | I allow multiple images per product (admin inline) |
| `Coupon` | cart | `code`, `discount_percent`, `active`, `valid_from`, `valid_to` | `is_valid()` checks the active flag + date window |
| `Order` | orders | `user` (FK), `coupon` (FK, nullable), `subtotal`, `discount`, `total`, `status`, `payment_method`, `payment_status`, `transaction_id`, `full_name`, `address`, `phone` | `status`: placed / processing / shipped / delivered / cancelled |
| `OrderItem` | orders | `order` (FK), `product` (FK, nullable), `product_name`, `size`, `price`, `quantity` | I snapshot name/price so history survives me editing/deleting a product later |

My entity relationships at a glance:

```
User ──1:1── Profile
Category ──1:N── Product ──1:N── ProductImage
Product ──M:N── ColorVariation
Product ──M:N── SizeVariation
User ──1:N── Order ──1:N── OrderItem ──N:1── Product
Order ──N:1── Coupon (optional)
```

---

## 8. My URL Map

| URL | View | App | Auth required |
|---|---|---|---|
| `/` | `index` | home | No |
| `/products/<slug>/` | `get_product` | products | No |
| `/accounts/register/` | `register_page` | accounts | No |
| `/accounts/login/` | `login_page` | accounts | No |
| `/accounts/activate/<email_token>/` | `activate_email` | accounts | No |
| `/accounts/logout/` | `logout_user` | accounts | Yes (implicitly) |
| `/cart/` | `cart_detail` | cart | No |
| `/cart/add/<slug>/` | `cart_add` (POST) | cart | No |
| `/cart/update/<key>/` | `cart_update` (POST) | cart | No |
| `/cart/remove/<key>/` | `cart_remove` | cart | No |
| `/cart/coupon/apply/` | `cart_apply_coupon` (POST) | cart | No |
| `/cart/coupon/remove/` | `cart_remove_coupon` | cart | No |
| `/cart/wishlist/` | `wishlist_detail` | cart | No |
| `/cart/wishlist/toggle/<slug>/` | `wishlist_toggle` | cart | No |
| `/checkout/` | `checkout` | orders | **Yes** |
| `/checkout/success/<uuid:order_id>/` | `order_success` | orders | **Yes** |
| `/checkout/history/` | `order_list` | orders | **Yes** |
| `/payments/initiate/<uuid:order_id>/` | `initiate_payment` | payments | **Yes** |
| `/payments/success/`, `/fail/`, `/cancel/`, `/ipn/` | payment callbacks | payments | No (gateway calls these) |
| `/admin/` | Django admin | — | Superuser |

---

## 9. How I Configured Settings & Environment

Right now everything lives in `ecomm/settings.py`, which was fine while I was building
this. Before I take this beyond local development, I plan to pull the sensitive values
out into environment variables, e.g.:

```python
import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-only-insecure-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

SSLCOMMERZ_STORE_ID = os.environ.get('SSLCOMMERZ_STORE_ID', '')
SSLCOMMERZ_STORE_PASSWORD = os.environ.get('SSLCOMMERZ_STORE_PASSWORD', '')
SSLCOMMERZ_IS_SANDBOX = os.environ.get('SSLCOMMERZ_IS_SANDBOX', 'True') == 'True'
```

Then I'll set the actual values as OS/host environment variables (or a `.env` file
loaded with `python-dotenv`) instead of committing them to source control.

Key settings I keep in mind:

- `MEDIA_ROOT` / `MEDIA_URL` — my uploaded images (`public/static/`, served at
  `/media/`).
- `STATIC_ROOT` / `STATIC_URL` — my CSS/JS assets, collected into `staticfiles/` for
  production via `collectstatic`.
- `TEMPLATES → OPTIONS → context_processors` — includes `cart.context_processors.cart`
  and `.wishlist`, which is how my cart/wishlist counts show up sitewide.

---

## 10. How I Use the Admin Panel

I log in at `/admin/` with my superuser account. Here's what I registered per app:

- **Accounts** → `Profile` (I toggle `is_email_verified` here to manually activate a
  user without email).
- **Products** → `Category`, `Product` (with inline `ProductImage` upload),
  `ColorVariation`, `SizeVariation`.
- **Cart** → `Coupon` (I create/deactivate discount codes and set validity windows
  here).
- **Orders** → `Order` (with inline, read-only `OrderItem` rows) — I can filter by
  `status`, search by username or shipping name, and update `status` here as an order
  moves through fulfillment (processing → shipped → delivered).
- **Payments** — I didn't register any models here; nothing to manage, since payment
  state lives on `Order`.

---

## 11. The Workflows I Designed

### Sign-up → verified login
1. A user submits my register form → I create a `User` + `Profile`, and send the
   activation email (or print it to console, depending on `EMAIL_BACKEND`).
2. They click the emailed link → `activate_email` flips `Profile.is_email_verified`.
3. They log in → `login_page` checks the verified flag before I allow
   `authenticate()`/`login()`.

### Browse → add to cart → checkout
1. `home.index` or `products.get_product` — I let them browse/search/view a product
   (optionally picking a size, which updates the displayed price).
2. `cart.cart_add` (POST) — adds the product+size to the session cart, or jumps
   straight to checkout if they used "Buy Now."
3. `cart.cart_detail` — they review the cart, update quantities, apply a coupon.
4. `orders.checkout` (login required) — they enter shipping info and choose Cash on
   Delivery or Online Payment → I create the `Order` + `OrderItem`s, then clear the
   cart.
5. **COD** → straight to `orders.order_success`.
   **Online** → `payments.initiate_payment` → SSLCommerz hosted page → gateway
   redirects back to `payment_success`/`fail`/`cancel`, which I use to update
   `Order.payment_status`, then on to `order_success` or `order_list`.

### Wishlist
`cart.wishlist_toggle` adds/removes a product slug from the session wishlist;
`wishlist_detail` renders the saved products.

---

## 12. Problems I Ran Into (and How I Fixed Them)

| Symptom | What was going on / how I fixed it |
|---|---|
| `No module named 'django'` | My virtual environment wasn't activated, or I forgot to run `pip install -r requirements.txt`. |
| Couldn't log in after registering | My account wasn't email-verified yet. I checked my console (since I was using the console email backend) for the activation link, or verified it manually in `/admin/` under `Profile`. |
| Images weren't showing on the site | I confirmed `DEBUG=True` in dev (media is only auto-served by Django when `DEBUG` is on) and made sure I actually uploaded images through `/admin/`, not just dropped files on disk. |
| `django.db.utils.OperationalError: no such table` | I hadn't applied migrations yet — ran `python manage.py makemigrations && python manage.py migrate`. |
| Emails weren't sending | Real Gmail SMTP needs an **App Password**, not my normal password, and I had to uncomment and fill in `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`. For local dev, I just switch to the console backend instead. |
| "Online payment is not configured yet" message | I'd left `SSLCOMMERZ_STORE_ID` / `SSLCOMMERZ_STORE_PASSWORD` blank — I either register a free sandbox store or just use Cash on Delivery. |
| Coupon wouldn't apply | I checked in `/admin/` that the `Coupon` was `active` and, if set, that today's date fell within `valid_from`/`valid_to`. |
| `CSRF verification failed` on payment callback pages | Those views are intentionally `@csrf_exempt` since SSLCommerz posts from an external domain — if I see this error elsewhere, it's unrelated to my payment flow. |

---

## 13. How I Plan to Deploy This

I know this ships with development-friendly defaults, and here's my checklist for
before I take it live:

1. Set `DEBUG = False` and populate `ALLOWED_HOSTS` with my real domain(s).
2. Replace my hardcoded `SECRET_KEY` with a securely generated one from an environment
   variable.
3. Move to a production-grade database (PostgreSQL/MySQL) instead of SQLite once I
   expect concurrent traffic.
4. Serve static files via `collectstatic` + a static file host/CDN or WhiteNoise —
   Django's built-in static serving is dev-only.
5. Serve media (`MEDIA_ROOT`) from cloud storage (e.g. S3), since local disk storage
   won't survive a typical container redeploy.
6. Put real SMTP credentials and SSLCommerz **live** (non-sandbox) credentials into
   environment variables, and set `SSLCOMMERZ_IS_SANDBOX = False`.
7. Put the app behind HTTPS and a WSGI server (Gunicorn/uWSGI) + reverse proxy
   (Nginx), instead of `runserver`.

---

## 14. What I'd Still Like to Improve

Things I'm aware of in my current codebase, so I don't forget about them if I extend
this later or hand it off to someone else:

- **I don't independently verify payment success yet.** My `payment_success` view
  currently trusts the browser redirect's POST data. Before I mark an order `paid` in
  production, I need to call SSLCommerz's *Order Validation API* with `val_id`
  (I already left myself a `NOTE` comment about this in `payments/views.py`), and/or
  lean primarily on the `payment_ipn` webhook. Right now my fail/cancel views also
  don't verify the request actually came from SSLCommerz, and anyone can hit those
  callback URLs directly since I haven't restricted them to the gateway.
- **I haven't added stock/inventory tracking.** My `Product` model has no quantity
  field, so nothing stops me from overselling, and I have no low-stock or
  out-of-stock display logic yet.
- **My guest cart & wishlist are session-only.** They're lost if someone clears
  cookies or switches devices, and I haven't built any "merge guest cart into account
  on login" logic.
- **I don't have automated tests yet** for `products`/`home` beyond the default stub
  (`tests.py` is still empty boilerplate in most of my apps).
- **I left some unused imports in `accounts/views.py`** — `from cmath import log` and
  `from tkinter import E` — I should clean those out.
- **I haven't rate-limited passwords/emails**, so my login/register endpoints could be
  targeted for brute-forcing until I add something like `django-axes` or a CAPTCHA.