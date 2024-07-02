import unittest
from app import create_app, db
from product.product_models import Product
import json

class ProductCrudTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.create_roles_and_user()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()



    def login(self):
        return self.client.post('/api/login', data=json.dumps({'email': 'test@test.com', 'password': 'password'}), content_type='application/json')

    def test_create_product(self):
        self.login()
        response = self.client.post('/api/products', data=json.dumps({'name': 'Test Product', 'description': 'Test Description', 'price': 19.99}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Product created successfully', str(response.data))

    def test_get_products(self):
        self.login()
        self.client.post('/api/products', data=json.dumps({'name': 'Test Product', 'description': 'Test Description', 'price': 19.99}), content_type='application/json')
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Product', str(response.data))

    def test_get_product(self):
        self.login()
        response = self.client.post('/api/products', data=json.dumps({'name': 'Test Product', 'description': 'Test Description', 'price': 19.99}), content_type='application/json')
        product_id = json.loads(response.data)['product']['id']
        response = self.client.get(f'/api/products/{product_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Product', str(response.data))

    def test_update_product(self):
        self.login()
        response = self.client.post('/api/products', data=json.dumps({'name': 'Test Product', 'description': 'Test Description', 'price': 19.99}), content_type='application/json')
        product_id = json.loads(response.data)['product']['id']
        response = self.client.put(f'/api/products/{product_id}', data=json.dumps({'name': 'Updated Product', 'description': 'Updated Description', 'price': 29.99}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Product updated successfully', str(response.data))

    def test_delete_product(self):
        self.login()
        response = self.client.post('/api/products', data=json.dumps({'name': 'Test Product', 'description': 'Test Description', 'price': 19.99}), content_type='application/json')
        product_id = json.loads(response.data)['product']['id']
        response = self.client.delete(f'/api/products/{product_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Product deleted successfully', str(response.data))

if __name__ == '__main__':
    unittest.main()
