#---BY NGUYEN CHI CUONG ---

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- CẤU HÌNH APP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cuongmobile_vip_key' # Key bảo mật
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db' # Tên file database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- CẤU TRÚC DỮ LIỆU (DATABASE) ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(500))
    desc = db.Column(db.Text)
    screen = db.Column(db.String(100))
    cpu = db.Column(db.String(100))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.String(200))
    total_price = db.Column(db.Float)
    date_created = db.Column(db.DateTime, default=datetime.now)

# --- CÁC TRANG WEB (ROUTES) ---

@app.route('/')
def home():
    # Lấy tất cả sản phẩm từ database đưa ra trang chủ
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:id>')
def product_detail(id):
    # Xem chi tiết 1 sản phẩm
    product = Product.query.get_or_404(id)
    return render_template('detail.html', product=product)

@app.route('/cart')
def cart():
    # Trang giỏ hàng
    if 'cart' not in session: session['cart'] = []
    cart_items = []
    total = 0
    for pid in session['cart']:
        p = Product.query.get(pid)
        if p:
            cart_items.append(p)
            total += p.price
    return render_template('cart.html', items=cart_items, total=total)

@app.route('/add-to-cart/<int:id>')
def add_to_cart(id):
 
    if 'cart' not in session: session['cart'] = []
    session['cart'].append(id)
    return redirect(url_for('cart'))

@app.route('/clear-cart')
def clear_cart():

    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        total = float(request.form.get('total'))
        
        new_order = Order(customer_name=name, customer_phone=phone, 
                          customer_address=address, total_price=total)
        db.session.add(new_order)
        db.session.commit()
        session.pop('cart', None) 
        return render_template('invoice.html', order=new_order)

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        name = request.form['name']
        brand = request.form['brand']
        price = float(request.form['price'])
        image = request.form['image']
        desc = request.form['desc']
        screen = request.form['screen']
        cpu = request.form['cpu']
        
        new_p = Product(name=name, brand=brand, price=price, image=image, desc=desc, screen=screen, cpu=cpu)
        db.session.add(new_p)
        db.session.commit()
        return redirect(url_for('admin'))
        
    products = Product.query.all()
    return render_template('admin.html', products=products)


def create_sample_data():
    if not Product.query.first():
        p1 = Product(name="iPhone 15 Pro Max", brand="Apple", price=34990000, 
                     image="https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800",
                     desc="Vỏ Titan, Chip A17 Pro.", screen="6.7 inch", cpu="A17 Pro")
        p2 = Product(name="Samsung S24 Ultra", brand="Samsung", price=31990000, 
                     image="https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800",
                     desc="Galaxy AI đỉnh cao.", screen="6.8 inch", cpu="Snapdragon 8 Gen 3")
        db.session.add_all([p1, p2])
        db.session.commit()
        print("Đã tạo dữ liệu mẫu thành công!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        create_sample_data() 

    app.run(host='localhost', port=5555, debug=True)