import unittest
from app.main import create_app, db
from user.user_models import User
import json
from werkzeug.security import generate_password_hash
import ast
from flask_jwt_extended import create_access_token



class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.create_user()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_user(self):
        user = User(username='testuser', email='test@example.com', password=generate_password_hash('password'), role='seller')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id
        self.access_token = create_access_token(identity=self.user_id)


    def test_register_user(self):
        response = self.client.post('/users/register', data=json.dumps({
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'password',
            "role":'seller'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response = ast.literal_eval(response.data.decode("UTF-8"))
        self.assertIn('User created',response['message'])

        with self.app.app_context():
            user = User.query.filter_by(email='test2@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'testuser2')

    def test_login_user(self):
        response = self.client.post('/users/login', data=json.dumps({
            'username': 'testuser',
            'password': 'password'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = ast.literal_eval(response.data.decode("UTF-8"))
        self.assertIn('Logged In', str(response['message']))

    def test_login_user_invalid_password(self):
        response = self.client.post('/users/login', data=json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response = ast.literal_eval(response.data.decode("UTF-8"))
        self.assertIn("Invalid username or password",response['error'])

    def login(self):
        response = self.client.post('/users/login', data=json.dumps({
            'username': 'testuser',
            'password': 'password'
        }), content_type='application/json')


    def test_logout_user(self):
        self.login()
        headers = {'Authorization': f'{self.access_token}'}
        response = self.client.get('/users/logout',headers=headers)
        self.assertEqual(response.status_code, 200)
        response = ast.literal_eval(response.data.decode("UTF-8"))
        self.assertIn('token revoked successfully', response['message'])

    
    
    def test_list_users(self):
        self.login()
        headers = {'Authorization': f'{self.access_token}'}
        response = self.client.get('/users/list', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_get_user(self):
        self.login()
        headers = {'Authorization': f'{self.access_token}'}
        response = self.client.get(f'/users/{self.user_id}',headers=headers)
        self.assertEqual(response.status_code, 200)

    
    
    def test_update_user(self):
        self.login()
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.client.put(f'/users/{self.user_id}',data=json.dumps({
            'username': 'updateduser',
            'email': 'updated@example.com'
        }),headers=headers, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        self.login()
        headers = {'Authorization': f'{self.access_token}'}
        response = self.client.delete(f'/users/{self.user_id}',headers=headers)
        self.assertEqual(response.status_code, 200)
        response = ast.literal_eval(response.data.decode("UTF-8"))
        self.assertIn('"user deleted', response['message'])


    def test_deposit(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.client.post('/users/deposit/money', data=json.dumps({
            'amount': 50
        }), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Deposit successful', str(response.data))
        self.assertIn('"new_balance": 50', str(response.data))

    def test_invalid_deposit_amount(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.client.post('/users/deposit/money', data=json.dumps({
            'amount': -10
        }), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid amount', str(response.data))


if __name__ == '__main__':
    unittest.main()
