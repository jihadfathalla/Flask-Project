# Flask Project

This is a Flask-based web application with authentication, user management, and JWT-based token authentication.

## Features

- User registration
- User login
- User authorization
- JWT token authentication
- User management (CRUD operations)
- Deposit money to user account

## Requirements

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:

    ```bash
    git clone [https://github.com/jihadfathalla/Gehad-BackendTask]
    cd flask
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:

    - On Windows:

      ```bash
      venv\Scripts\activate
      ```

    - On macOS/Linux:

      ```bash
      source venv/bin/activate
      ```

4. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Set up the environment variables:

    - Create a `.env` file in the root directory of the project and add the following variables:

      ```env
      SECRET_KEY=your_secret_key
      SQLALCHEMY_DATABASE_URI=sqlite:///site.db
      JWT_SECRET_KEY=your_jwt_secret_key
      ```

6. Initialize the database:

    ```bash
    python create_db.py
    ```

## Running the Application

1. Ensure the virtual environment is activated.

2. Run the Flask application:

    ```bash
    python run.py
    ```

3. Open your web browser and navigate to `http://127.0.0.1:5000`.

## API Endpoints

### Authentication

- **POST /users/register**

  Register a new user.

  ```json
  {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password",
    "role":"buyer"
  }
