from flask import Flask,jsonify,request
from app.config import db , jwt ,login_manager
from user.user_models import User, TokenBlocklist
from user import user_routes
from user import user_models
from user.user_routes import auth_bp 
from product.product_routes import product_bp
from flasgger import Swagger
from flasgger import LazyString, LazyJSONEncoder
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config["SWAGGER"] = {"title": "Swagger-UI", "uiversion": 2}
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('FLASK_SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY']== os.getenv('FLASK_SECRET_KEY')
    app.config['DEBUG']= os.getenv('FLASK_DEBUG')
    app.config['SQLALCHEMY_ECHO']=os.getenv('FLASK_SQLALCHEMY_ECHO')
    app.config['JWT_SECRET_KEY']=os.getenv('FLASK_JWT_SECRET_KEY')



    # initialize exts
    db.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)


    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/users")
    app.register_blueprint(product_bp, url_prefix="/products")

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_headers, jwt_data):
        identity = jwt_data["sub"]

        return User.query.filter_by(username=identity).one_or_none()

    # additional claims

    
    @jwt.additional_claims_loader
    def make_additional_claims(identity):
        if identity == "janedoe123":
            return {"is_staff": True}
        return {"is_staff": False}

    # jwt error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Request doesnt contain valid token",
                    "error": "authorization_header",
                }
            ),
            401,
        )
    
    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header,jwt_data):
        jti = jwt_data['jti']

        token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()

        return token is not None

        
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        # "static_folder": "static",  # must be set by user
        "swagger_ui": True,
        "specs_route": "/swagger/",
    }

    template = dict(
        swaggerUiPrefix=LazyString(lambda: request.environ.get("HTTP_X_SCRIPT_NAME", ""))
    )

    app.json_encoder = LazyJSONEncoder
    swagger = Swagger(app, config=swagger_config, template=template)

        
    return app