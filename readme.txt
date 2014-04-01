Ryan Luo
ryan.luo@pomona.edu

Flask Application
hosted at: http://databasesystems6.herokuapp.com

database: There is no sql file because Flask does not take a sql file. 
The database is shown below. Each column is labeled as a column, and
relationship is essentially a foreign key reference.

There is no need to run this application locally. Simply type in the 
above url. Parts a-e are all clearly labeled on the web application. 


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



