from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import User


def user_response(user):
    return {"id": user.id, "username": user.username}


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        password = data.get("password")
        if not password:
            return {"errors": ["Password is required."]}, 422
        if password != data.get("password_confirmation"):
            return {"errors": ["Passwords do not match."]}, 422

        try:
            user = User(username=data.get("username"))
            user.password = password
            db.session.add(user)
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            return {"errors": [str(error)]}, 422
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username is already taken."]}, 422

        session["user_id"] = user.id
        return user_response(user), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        user = User.query.filter_by(username=data.get("username")).first()
        if user and user.authenticate(data.get("password") or ""):
            session["user_id"] = user.id
            return user_response(user), 200
        return {"errors": ["Invalid username or password."]}, 401


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        return user_response(user) if user else {}, 200


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 200


def register_auth_resources(api):
    api.add_resource(Signup, "/signup", endpoint="signup")
    api.add_resource(Login, "/login", endpoint="login")
    api.add_resource(CheckSession, "/check_session", endpoint="check_session")
    api.add_resource(Logout, "/logout", endpoint="logout")
