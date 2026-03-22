from datetime import datetime
from flask import render_template, request, redirect, session, url_for, flash
from ReikiNikki import app
from ReikiNikki.models import SessionLocal, Product, Order, AdminUser
import stripe
import os
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

#Index page
@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='NickiReiki',
        year=datetime.now().year,
    )

#Contact page
@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )
#About page
@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

#Product page
@app.route('/product/<int:id>')
def product_page(id):
    db = SessionLocal()
    product = db.query(Product).get(id)
    return render_template('product.html', product=product)

#Add to cart
@app.route('/add-to-cart/<int:id>')
def add_to_cart(id):
    cart = session.get("cart", [])
    cart.append(id)
    session["cart"] = cart
    return redirect(url_for('cart'))

#Cart
@app.route('/cart')
def cart():
    db = SessionLocal()
    cart_ids = session.get("cart", [])
    products = db.query(Product).filter(Product.id.in_(cart_ids)).all()
    total = sum(p.price for p in products)
    return render_template('cart.html', products=products, total=total)

#Checkout Stripe
@app.route('/checkout', methods=['POST'])
def checkout():
    db = SessionLocal()
    cart_ids = session.get("cart", [])
    products = db.query(Product).filter(Product.id.in_(cart_ids)).all()
    total = sum(p.price for p in products)

    session_stripe = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "sek",
                "product_data": {"name": "Order"},
                "unit_amount": int(total * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="https://din-sida.se/success",
        cancel_url="https://din-sida.se/cancel",
    )

    return redirect(session_stripe.url)


#Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = SessionLocal()
        user = db.query(AdminUser).filter_by(username=username).first()

        if user and user.password == password:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Fel användarnamn eller lösenord")

    return render_template('admin/login.html')

#Amin protection
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for('admin_login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

#Admin dashboard
@app.route('/admin')
@admin_required
def admin_dashboard():
    db = SessionLocal()
    products = db.query(Product).all()
    orders = db.query(Order).all()
    return render_template('admin/dashboard.html', products=products, orders=orders)

#Create new product
@app.route('/admin/new-product', methods=['GET', 'POST'])
@admin_required
def admin_new_product():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        image = request.form['image']  # eller filuppladdning

        db = SessionLocal()
        product = Product(title=title, description=description, price=price, image=image)
        db.add(product)
        db.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('admin/new_product.html')

#Show Orders
@app.route('/admin/orders')
@admin_required
def admin_orders():
    db = SessionLocal()
    orders = db.query(Order).all()
    return render_template('admin/orders.html', orders=orders)

