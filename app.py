from flask import Flask, flash, render_template, session, url_for, request, redirect, g, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os
import unicodedata
import urllib, hashlib
import datetime, operator

app = Flask(__name__)
app.secret_key = "some_"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"


db = SQLAlchemy(app)
def uni(x):
    return unicodedata.normalize('NFKD',x).encode('ascii','ignore')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


def uniquifyo(xl):
    final = []
    ranked = {}
    for x in xl:
        if x in ranked:
            ranked[x] += 1
            continue
        ranked[x] = 1
    sorted_x = sorted(ranked.iteritems(), key=operator.itemgetter(1),reverse=True)
    for y in sorted_x:
        final.append(y[0])
    return final

class Product(db.Model):
    model = db.Column(db.Integer, primary_key=True)
    maker = db.Column(db.String(80), unique=False)
    type = db.Column(db.String(120), unique = False)
    PC = db.relationship('PCs',backref='product',lazy='dynamic')
    printer = db.relationship('Printers',backref='product',lazy='dynamic')
    laptop = db.relationship('Laptops',backref='product',lazy='dynamic')
    
    
    def is_authenticated(self):
        return True
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
    
	
    def __init__(self, model, maker, type):
        self.model = model 
        self.maker = maker 
        self.type = type 

    def __repr__(self):
        return "<Product %r>" % self.model

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80))

    def __repr__(self):
        return "<File %r>" % self.filename
    
class PCs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    speed = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    hd = db.Column(db.Integer)
    price = db.Column(db.Integer)
    model = db.Column(db.Integer, db.ForeignKey('product.model'))
 
    def __repr__(self):
        return "<PC %r>" % self.model
	
class Laptops(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    speed = db.Column(db.Integer)
    ram = db.Column(db.Integer)
    hd = db.Column(db.Integer)
    screen = db.Column(db.Integer)
    price = db.Column(db.Integer)
    model = db.Column(db.Integer, db.ForeignKey('product.model'))

    
    def __repr__(self):
        return "<Laptops %r>" % self.model

class Printers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.Boolean)
    type = db.Column(db.String(80))
    price = db.Column(db.Integer)
    model = db.Column(db.Integer, db.ForeignKey('product.model'))

    def __repr__(self):
        return "< Printers %r>" % self.model


   


@app.route("/")
def index():
    return render_template("new.html")


@app.route("/closestPrice",methods=["GET","POST"])
def closestprice():
    p = int(request.form["price"])
    pcs = db.session.query(PCs)
    mypc = pcs.get(1)
    price = abs(mypc.price-p)
    for pc in pcs: 
	    if price > abs(pc.price-p):
		   mypc = pc 
		   price = pc.price-p
    product = mypc.product
    return render_template("closestPrice.html",pc=mypc,product=product)
    
@app.route("/minlaptop",methods=["GET","POST"])
def minlaptop():
    speed = int(request.form["speed"])
    ram = int(request.form["ram"])
    hd = int(request.form["hd"])
    screen = int(request.form["screen"])
    laptops = db.session.query(Laptops).filter(Laptops.speed>=speed,Laptops.ram>=ram,Laptops.hd>=hd,Laptops.screen>=screen)
    products=[]
    for laptop in laptops:
	   products.append(laptop.product)
    products = zip(laptops,products)
    return render_template("minLaptop.html",products=products)

@app.route("/manufacturer",methods=["GET","POST"])
def manufacturer():
    products = []
    maker = request.form["maker"]
    products1 = db.session.query(Product).join(PCs,Product.model==PCs.model).filter(Product.maker==maker)
    pcs = db.session.query(PCs).join(Product,Product.model==PCs.model).filter(Product.maker==maker)
    products1 = zip(pcs,products1)
    products2 = db.session.query(Product).join(Laptops,Product.model==Laptops.model).filter(Product.maker==maker)
    laptops = db.session.query(Laptops).join(Product,Product.model==Laptops.model).filter(Product.maker==maker)
    products2 = zip(laptops,products2)
    products3 = db.session.query(Product).join(Printers,Product.model==Printers.model).filter(Product.maker==maker)
    printers = db.session.query(Printers).join(Product,Product.model==Printers.model).filter(Product.maker==maker)
    products3 = zip(printers,products3)
    return render_template("manufacturer.html",products1 = products1, products2 = products2, products3 = products3)
    
@app.route("/system",methods=["GET","POST"])
def system():
    printers = db.session.query(Printers).order_by(Printers.price)
    pcs = db.session.query(PCs).order_by(PCs.price)
    budget = request.form["budget"]
    speed = int(request.form["speed"])
    price = printers[0].price+pcs[0].price
    printer = printers[0]
    counter = 0;
    mypc = pcs[0]
    for pc in pcs :
	mypc = pc
	if speed <= pc.speed :
		break 
    printers = list(printers)
	
    while (price <= budget) and counter < len(printers) and not (printer.color) :
        counter += 1
	printer = printers[counter]
	price = mypc.price + printer.price
    print(printer.price)
    print(mypc.price)
    return render_template("system.html",printer = printer, pc = mypc)

@app.route("/newPC",methods=["GET","POST"])
def newPC():
     m = request.form["maker"]
     n = int(request.form["model"])
     s = int(request.form["speed"])
     r = int(request.form["ram"])
     h = int(request.form["hd"])
     p = int(request.form["price"])

     pcs = list(PCs.query.filter_by(model=n).all())
     if pcs == []:
	pr = Product(model=n,maker=m,type="PC")
	pc = PCs(speed=s,ram=r,hd=h,price=p,product=pr)
	db.session.add(pr)
	db.session.add(pc)
	try: 
	    db.session.commit()
	    flash("Successfully added pc")
	    return redirect("/")
    	except Exception as e:
            db.session.rollback()
	    flash("Problem adding to database")
	    return redirect("/")
     flash("Model # not unique")
     return redirect("/")

@app.route("/sresults",methods=["GET","POST"])
def sresults():
    t = request.form["type"]
    p = request.form["price"]
    speed = request.form["speed"]
    ram = request.form["ram"]
    hd = request.form["hd"]
    screen = request.form["screen"]
    maker = request.form["maker"]
    model = request.form["model"]
    print(t+p+speed+ram+hd+screen+maker+model);
        
    pcs = []
    products = []
    if t=="PCs" : 
	pcs = db.session.query(PCs).filter(p>=PCs.price).all()
	for pc in pcs:
		products.append(pc.product)

	products = zip(products,pcs)
    '''for sch in schools:
        users += User.query.filter_by(school=sch).all()
    for sk in skills:
        skillList = Skills.query.filter_by(skill=sk).all()
        for s in skillList:
            users.append(s.user)

    users = uniquifyo(users)
    names = []
    for user in users:
        names.append(uni(user.username))
	'''
    names = []
    return render_template('sresults.html',products=products)


if __name__ == "__main__":
    db.session.rollback()
    db.create_all()

    # try:
    #     x = User("test3", "test2@gmail.com", "password")
    #     db.session.add(x)
    #     db.session.commit()
    #     print "worked"
    # except IntegrityError:
    #     print "Not Working"
    app.run(debug=True)
