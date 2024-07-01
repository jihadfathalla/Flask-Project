from main import app, db
from models import User, Role

def load_initial_data():
    # Create roles
    buyer_role = Role(name='buyer')
    seller_role = Role(name='seller')

    # Add to session
    db.session.add(buyer_role)
    db.session.add(seller_role)

    # Commit session
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
        load_initial_data()
