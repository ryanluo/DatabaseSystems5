from app import db,Product,Laptops,Printers,PCs
import random

m = ["Apple","Google","HP","Lenovo","Sony","Samsung"]
t = ["ink-jet","laser"]

for i in range(11,100):
	p = Product(model=i,maker = m[random.randint(0,5)], type = "laptop")
	db.session.add(p)
	db.session.add(Laptops(speed=random.randint(2,16),ram=random.randint(2,16),hd=random.randint(256,2048),screen=random.randint(10,20),price=random.randint(500,10000),product=p))
db.session.commit()

for j in range(101,200):
	p = Product(model=j,maker = m[random.randint(0,5)], type = "pc")
	db.session.add(p)
	db.session.add(PCs(speed=random.randint(2,16),ram=random.randint(2,16),hd=random.randint(256,2048),price=random.randint(500,10000),product=p))
	
for k in range(201,300):
	p = Product(model=k,maker = m[random.randint(0,5)], type = "printer")
	db.session.add(p)
	c = (k%2==0)
	db.session.add(Printers(color=c,type=t[random.randint(0,1)],price=random.randint(500,10000),product=p))

db.session.commit()



