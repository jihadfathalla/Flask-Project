from app.config import db



class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    amount_available = db.Column(db.Float, nullable=True)
    cost  = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)



    def __repr__(self):
        return f"Product('{self.product_name}', {self.cost})"
