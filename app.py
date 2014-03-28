from flask import Flask, flash, render_template, session, url_for, request, redirect, g, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from forms import LoginForm
from flask.ext.openid import OpenID
import os
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
import unicodedata
import urllib, hashlib
import datetime, operator
from werkzeug import secure_filename

UPLOAD_FOLDER='/static'
ALLOWED_EXTENSIONS=set(['txt','pdf','doc','odt', "docx"])
app = Flask(__name__)
app.secret_key = "some_"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

app.config['DEFAULT_FILE_STORAGE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') + UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
loggedUser =  None
curID = None
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


   

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.route("/")
def index():
    # return str(User.query.all()[0].password) # I don't think this will 
    curUsername = None
    if loggedUser:
        curUsername = loggedUser.username.encode("utf-8")
    return render_template("new.html")

@app.route("/signup")
def signup():
    if loggedUser:
        return redirect("/")
    return render_template("signup.html")

@app.route("/signup/college",  methods=["POST", "GET"])
def collegesignup():
    if loggedUser:
        return redirect("/")
        
        # c2 = request.form["company2"]
        # c3 = request.form["company3"]

        
        # t2 = request.form["title2"]
        # t3 = request.form["title3"]


        # s1 = request.form["startdate1"]
        
        # s2 = request.form["startdate2"]
        # s3 = request.form["startdate3"]

        # e1 = request.form["enddate1"]
        # e2 = request.form["enddate2"]
        # e3 = request.form["enddate3"]

      
              
    return render_template("new.html")



@app.route('/signin', methods = ["GET", "POST"])
def signin():
    if loggedUser:
            return redirect('/settings/'+ loggedUser.username.encode("utf-8"))
    if request.method == "POST":

        error = None
        form = LoginForm()
        theUser = request.form["username"].lower()
        password = request.form["password"].lower()
        print theUser
        for users in User.query.all():
            error = None
            if theUser == users.email:

                if password == users.password:
                    curID = users.id
                    global loggedUser
                    loggedUser = users

                    user = load_user(users.id)
                    login_user(user)
                    flash('Logged ' + theUser + ' in successfully.')
                    return redirect('/settings/'+ users.username)
                else: 
                    error = "Invalid username and password combination." 
                    return render_template("signin.html", error = error)     
        error = "Invalid username and password combination."
        return render_template("signin.html", error = error) 
    return render_template("signin.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    global loggedUser
    loggedUser = None
    return redirect('/')

@app.route("/settings/<username>", methods=['GET', 'POST'])
@login_required
def settings(username):
    if request.method=='POST':
        file = request.files['file']
        u = User.query.filter_by(username=username).first()
        if file and allowed_file(file.filename):
            filename = secure_filename(str(loggedUser.id) + file.filename[file.filename.rfind("."):])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            f = File(filename=filename,user=u)
            db.session.add(f)
            db.session.commit()
            return redirect("/settings/"+username)        
    if loggedUser == None:
        return redirect("/signin")
    if username == loggedUser.username.encode("utf-8"):
        if User.query.get(current_user.get_id()).role == "developer":
            cS = []
            cR = []
            s = []
            exp =[]
            f=[]
            user = User.query.filter_by(username=username).first()
            email = user.email.encode("utf-8").lower()
            size = 150
            default = "http://www.blackdogeducation.com/wp-content/uploads/facebook-default-photo.jpg"

            gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest()
            gravatar_url += urllib.urlencode({'default':default, 's':str(size)})

            
            skill = user.skills.all()
            files = user.files.all()
            conversationsS = Conversation.query.filter_by(user1=unicodedata.normalize('NFKD',user.username).encode('ascii','ignore')).all()
            conversationsR = Conversation.query.filter_by(user2=unicodedata.normalize('NFKD',user.username).encode('ascii','ignore')).all()
            experience = user.experience.all()
            for c in conversationsS:
                cS.append({'user': uni(c.user2), 'subject': uni(c.subject), 'timestamp': c.timestamp, 'id': c.id})
            for c in conversationsR:
                cR.append({'user': uni(c.user1), 'subject': uni(c.subject), 'timestamp': c.timestamp, 'id': c.id})
            for SKILLS in skill:
                s.append(unicodedata.normalize('NFKD',SKILLS.skill).encode('ascii','ignore'))
            for fil in files:
                f.append(fil.filename.encode("utf-8"))
            for exper in experience:
                exp.append({"title" : exper.title.encode("utf-8"), "company" : exper.company.encode("utf-8"), "description" : exper.description.encode("utf-8")})
            return render_template("settings.html",username=username,s=s,cS=cS,cR=cR, experience = exp, profpic = gravatar_url, files = f)
        else:
            cS = []
            cR = []
            s = []
            user = User.query.filter_by(username=username).first()

            conversationsS = Conversation.query.filter_by(user1=unicodedata.normalize('NFKD',user.username).encode('ascii','ignore')).all()
            conversationsR = Conversation.query.filter_by(user2=unicodedata.normalize('NFKD',user.username).encode('ascii','ignore')).all()
            for c in conversationsS:
                cS.append({'user': uni(c.user2), 'subject': uni(c.subject), 'timestamp': c.timestamp, 'id': c.id})
            for c in conversationsR:
                cR.append({'user': uni(c.user1), 'subject': uni(c.subject), 'timestamp': c.timestamp, 'id': c.id})
            user = User.query.filter_by(username=username).first()

            return render_template("company-settings.html",username=username,s=s,cS=cS,cR=cR)
    else:
        return redirect("/")
@app.route("/conversation/<ID>/<user>")
@login_required
def conversation(ID,user):
    c = Conversation.query.get(ID)
    subject = uni(c.subject)
    m=[]
    messages = c.messages.all()
    for M in messages:
        m.append({'sender':uni(M.sender),'body':uni(M.body),'timestamp':M.timestamp})
    return render_template("conversation.html",m=m,user=user,subject=subject,ID=ID)

@app.route("/reply/<ID>/<user>",methods=["GET"])
@login_required
def reply(ID,user):
    c = Conversation.query.get(ID)
    subject = uni(c.subject)

    return render_template("reply.html",ID=ID,user=user)

@app.route("/replying",methods=["GET","POST"])
@login_required
def replying():
    ID = request.form['conversation']
    Body = request.form['body']
    user = request.form['user']
    c = Conversation.query.get(ID)
    if uni(c.user2) == user: Sender = uni(c.user1)
    else: Sender = uni(c.user2)
    m = Message(sender=Sender,body=Body,timestamp=datetime.datetime.utcnow(),conversation=c)
    db.session.add(m)
    try:
        db.session.commit()
    except Exception as e:
            db.session.rollback()
            return "brokenm"
    return redirect('settings/'+Sender)
        
@app.route("/search",methods=["GET","POST"])
def search():
    schools = []
    users = User.query.all()
    for user in users:
        if uni(user.school) == "" : continue
        schools.append(uni(user.school))
    schools = list(set(schools))
    return render_template('search.html',schools=schools)

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

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method=='POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(loggedUser.email.encode("utf-8") + file.filename[file.filename.rfind("."):])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
	    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/start",methods=["GET","POST"])
@login_required
def start():
    Sender = request.form["user"];
    Receiver = request.form["to"]
    if User.query.filter_by(username=Receiver).first() == None: return "Invalid User!"
    Subject = request.form["subject"]
    body = request.form["body"]
    c =  Conversation(subject=Subject,user1=Sender,user2=Receiver,timestamp=datetime.datetime.utcnow())
    db.session.add(c)
    try :
        db.session.commit()
        m  = Message(sender=Sender,body=body,timestamp=datetime.datetime.utcnow(),conversation=c)
        db.session.add(m)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return "brokenm"         
    except Exception as e:
        db.session.rollback()
        return "brokenc" 
    
    return redirect('/settings/'+Sender)



@app.route("/converse/<username>",methods=["GET"])
@login_required
def converse(username):
    return render_template("compose.html",username=username)
@app.route("/profile/<username>")
@login_required 
def profile(username):

    if User.query.get(current_user.get_id()).role == "developer":

        cS = []
        cR = []
        s = []
        exp = []
        user = User.query.filter_by(username=username).first()
        skill = user.skills.all()
        experience = user.experience.all()
        files = user.files.all()[0]
        files = files.filename.encode("utf-8")
        for SKILLS in skill:
            s.append(unicodedata.normalize('NFKD',SKILLS.skill).encode('ascii','ignore'))
        for exper in experience:
            exp.append({"title" : exper.title.encode("utf-8"), "company" : exper.company.encode("utf-8"), "company" : exper.company.encode("utf-8")})


        return render_template("profile.html",user = user, username=username,s=s, experience = exp, f =files)
    else:
        return "not setup yet"


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
