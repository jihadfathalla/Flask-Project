from flask import Flask, jsonify
from extensions import db , jwt
from user import routes
from flask_login import LoginManager, UserMixin
from user import models

# from users import user_bp
# from models import User, TokenBlocklist
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)

    app.config.from_prefixed_env()

    # initialize exts
    db.init_app(app)
    jwt.init_app(app)
    login_manager = LoginManager(app)


    # register bluepints
    app.register_blueprint(routes.auth_bp, url_prefix="/auth")
    # app.register_blueprint(user_bp, url_prefix="/users")

    # # load user
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    # # additional claims

    
    # @jwt.additional_claims_loader
    # def make_additional_claims(identity):
    #     if identity == "janedoe123":
    #         return {"is_staff": True}
    #     return {"is_staff": False}

    # # jwt error handlers

    # @jwt.expired_token_loader
    # def expired_token_callback(jwt_header, jwt_data):
    #     return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

    # @jwt.invalid_token_loader
    # def invalid_token_callback(error):
    #     return (
    #         jsonify(
    #             {"message": "Signature verification failed", "error": "invalid_token"}
    #         ),
    #         401,
    #     )

    # @jwt.unauthorized_loader
    # def missing_token_callback(error):
    #     return (
    #         jsonify(
    #             {
    #                 "message": "Request doesnt contain valid token",
    #                 "error": "authorization_header",
    #             }
    #         ),
    #         401,
    #     )
    
    # @jwt.token_in_blocklist_loader
    # def token_in_blocklist_callback(jwt_header,jwt_data):
    #     jti = jwt_data['jti']

    #     token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()

    #     return token is not None

    return app