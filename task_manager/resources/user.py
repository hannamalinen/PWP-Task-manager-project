"""This module contains the User resource class and its methods"""
import uuid
from flask import request
from flask_restful import Resource
from task_manager.models import User
from task_manager import db


class UserItem(Resource):
    " Resource class for get, put, delete methods for User"

    # getting a user
    def get(self, unique_user):
        """Get a user by its unique id"""
        user = User.query.filter_by(unique_user=unique_user).first()
        if not user:
            return {"error": "User not found"}, 404
        return {
            "name": user.name,
            "email": user.email,
            "unique_user": user.unique_user
        }, 200


    def put(self, unique_user):

        "Updates a user's information"

        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        data = request.get_json()
        user = User.query.filter_by(unique_user=unique_user).first()
        if not user:
            return {"error": "User not found"}, 404
        #valdating the data
        if "name" in data:
            if not isinstance(data["name"], str):
                return {"error": "Name must be a string"}, 400
            user.name = data["name"]

        if "email" in data:
            if not isinstance(data["email"], str):
                return {"error": "Email must be a string"}, 400
            user.email = data["email"]
        if "password" in data:
            if not isinstance(data["password"], str):
                return {"error": "Password must be a string"}, 400
            user.password = data["password"]

        db.session.commit()
        return {
            "message": "User updated successfully"       
        }, 200

    def delete(self, unique_user):
        "Deletes a user"
        user = User.query.filter_by(unique_user=unique_user).first()
        if not user:
            return {"error": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()

        return {}, 204

class UserCollection(Resource):

    "Resource class for get method for UserCollection"

    def get(self):
        """Get all users"""
        users = User.query.all()
        user_list = [{"id": user.id,
                      "unique_user": user.unique_user,
                      "name": user.name,
                      "email": user.email,
                      "password": user.password} for user in users]
        return user_list, 200

    def post(self):
        "Creates a new user, with name, email and password"
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        try:
            name = request.json["name"]
            email = request.json["email"]
            password = request.json["password"]
        except KeyError:
            return {"error": "Incomplete request - missing fields"}, 400
        new_uuid = str(uuid.uuid4())
        if User.query.filter_by(unique_user=new_uuid).first():
# if the uuid already exists, generate a new one
            new_uuid = str(uuid.uuid4())
        if User.query.filter_by(email=email).first():
            return {"error": "Email is already in use"}, 400
        user = User(name=name, unique_user=new_uuid, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return {
            "message": "User added successfully",
            "unique_user": new_uuid
        }, 201
