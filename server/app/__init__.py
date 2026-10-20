from flask import Flask, request, session
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api

from .config import DevelopmentConfig
from .extensions import bcrypt, db
from .resources import register_resources


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)
    bcrypt.init_app(app)
    CORS(app, supports_credentials=True, origins=app.config["CORS_ORIGINS"])

    api = Api(app)
    register_resources(api)

    @app.before_request
    def require_login():
        if request.method == "OPTIONS" or request.endpoint in {
            None,
            "static",
            "signup",
            "login",
            "check_session",
            "logout",
        }:
            return None

        if not session.get("user_id"):
            return {"errors": ["Unauthorized"]}, 401

    return app


app = create_app()
