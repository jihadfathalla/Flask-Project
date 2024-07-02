from flask import Blueprint, session, jsonify,request
from utils.role_required_decorator import role_required
from flasgger import Swagger
from flasgger.utils import swag_from
from flasgger import LazyString, LazyJSONEncoder

from schemas import UserSchema
from flask_jwt_extended import (
    get_jwt,
    create_access_token,
    create_refresh_token,
    jwt_required,
    current_user,
    get_jwt_identity,
)
from user.user_models import User, TokenBlocklist
from logs.logging_aspects import view_logging_aspect
from utils.exception_handler_decorator import handle_exceptions
from .user_constants import (
    USER_LOGGER,
    USER_LOG_FILE_PATH
)


auth_bp = Blueprint("auth", __name__)


@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@auth_bp.post("/register")
def register_user():
    """
    user register.

    body:
    username (text).
    password (text).
    email (email).
    role [buyer,seller]

    Returns:
    "success message":  User created  in success
    message error in fail if validation fails in deposit

    """
    data = request.get_json()

    user = User.get_user_by_username(username=data.get("username"))

    if user is not None:
        return jsonify({"error": "User already exists"}), 409

    if not data or 'username' not in data or 'password' not in data or 'email' not in data or 'role' not in data:
        return jsonify({"message": "please required fields(username,password,email,role)"}), 400
   
    if add_deposit(data.get('deposit', 0)):
        new_user = User(username=data.get("username"),
                        email=data.get("email"),
                        role=data.get('role'),
                        deposit= data.get('deposit', 0)
        )

        new_user.set_password(password=data.get("password"))

        new_user.save()

        return jsonify({"message": "User created"}), 201
    else:
        return jsonify({"error": "deposit can only with this values [0,5, 10, 20, 50, 100]"}), 400
        

@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@auth_bp.post("/login")
def login_user():
    """
    user login.

    body:
    username (text).
    password (text).

    Returns:
    "tokens":  access_token, refresh_token,200 in success
    message error in fail

    """
    data = request.get_json()

    user = User.get_user_by_username(username=data.get("username"))

    if user and (user.check_password(password=data.get("password"))):
        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)
        return (
            jsonify(
                {
                    "message": "Logged In",
                    "tokens": {"access": access_token, "refresh": refresh_token},
                }
            ),
            200,
        )
    return jsonify({"error": "Invalid username or password"}), 400

@auth_bp.get("/refresh")
@jwt_required()
def refresh_access():
    """
    get refresh token.
    Returns:
    "token": new_access_token
    """
    identity = get_jwt_identity()

    new_access_token = create_access_token(identity=identity)

    return jsonify({"access_token": new_access_token})


@auth_bp.get('/logout')
@jwt_required(verify_type=False) 
def logout_user():
    """
    user loggout.
    """
    jwt = get_jwt()

    jti = jwt['jti']
    token_type = jwt['type']

    token_b = TokenBlocklist(jti=jti)

    token_b.save()

    return jsonify({"message": "token revoked successfully"}) , 200


@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@auth_bp.get("/list")
@jwt_required()
def list_users():
    """
    list users.


    Returns:
    "tokens": list of all users
    """

    page = request.args.get("page", default=1, type=int)

    per_page = request.args.get("per_page", default=3, type=int)

    users = User.query.paginate(page=page, per_page=per_page)

    result = UserSchema().dump(users, many=True)

    return (
        jsonify(
            {
                "users": result,
            }
        ),
        200,
    )
    

@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@auth_bp.get("/current/user")
@jwt_required()
def get_current_user():
    """
    get current user.


    Returns:
    user name and email

    """
    return jsonify(
        {
            "message": "message",
            "user_details": {
                "username": current_user.username,
                "email": current_user.email,
            },
        }
    )

@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@auth_bp.get("/<int:user_id>")
@jwt_required()
def get(user_id):
    """
    get user by id .

    param :user_id

    Returns:
    "tokens":  user data in success
    message error in fail

    """
    user = User.query.get_or_404(user_id)
    return jsonify(UserSchema().dump(user))


@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@auth_bp.put("/<int:user_id>")
@jwt_required()
def update_user(user_id):
    """
    update user fields .

    param: user_id

    Returns:
    user with updated data in  success
    message error in fail

    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if add_deposit(data.get('deposit', 0)):
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.deposit = data.get('cost', user.deposit)
        user.role = data.get('role', user.role)
        
        if "password" in data:
            user.set_password(password=data.get("password"))

        user.save()

        return jsonify(UserSchema().dump(user))
    else:
        return jsonify({"error": "deposit can only with this values [0,5, 10, 20, 50, 100]"}), 400




@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@auth_bp.delete("/<int:user_id>")
@jwt_required()
def delete_user(user_id):
    """
    delete user .

    param :user_id

    Returns:
    success message in  in success
    message error in fail

    """
    user = User.query.get_or_404(user_id)
    user.delete()
    return jsonify(
        {
            "message": "user deleted"
        },
        200
    )
    
    
  
 
@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@role_required('buyer')
@auth_bp.post("/deposit/money")
def deposit_money():
    """
    make current user  with a “buyer” role can deposit 5, 10, 20, 50, and 100 cent coins into their vending machine account and update it's balance in user table.

    body:
    amount (float).

    Returns:
    the new balance in success
    message error in fail on error 

    """
    data = request.get_json()
    amount= data.get('amount')
    if add_deposit(amount, user=current_user):
        return jsonify(
        {
            "message": f"you balance now is {current_user.deposit}"
        },
        200
            )
    else:
        return jsonify({"error": "deposit can only with this values [0, 5, 10, 20, 50, 100]"}), 400

        
    

# @handle_exceptions
# @view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
# @role_required('buyer')
# @auth_bp.post("/reset/deposit")
# def reset_deposit():
#     data = request.get_json()
#     user = current_user
#     user.deposit = data['deposit']
#     user.save()
#     return jsonify(
#         {
#             "message": f"you balance now is {user.deposit}"
#         },
#         200
#     )
  
@handle_exceptions
@view_logging_aspect(USER_LOGGER, USER_LOG_FILE_PATH)
@role_required('buyer')
@auth_bp.post("/reset/deposit")
def reset_deposit():
    """
    make current user reset deposit balance( make it =0) in user table.

   .

    Returns:
    success message

    """
    user =current_user
    user.deposit= 0
    user.save()
    return jsonify(
        {
            "message": "you balance now is 0"
        },
        200
    )  




def add_deposit(value, user=None):
    """
    check money amount in [0,5, 10, 20, 50, 100]
    
    param : value:

    Returns:
    the True success
    messageFalse in fail

    """
    if value in [0,5, 10, 20, 50, 100]:
        if user:
            user.deposit= value
            user.save()
        return True
    else:
        return False
