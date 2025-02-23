from flask import request, Response, url_for, jsonify
from flask_restful import Resource
from task_manager.models import User
from task_manager import db
import uuid

class UserItem(Resource):

    def get(self):
        pass

    # adding a user
    def post(self):
        if not request.is_json:
            return "Request content type must be JSON", 415
        try:
            name = request.json["name"]
            email = request.json["email"]
            password = request.json["password"]
        except KeyError:
            return "Incomplete request - missing fields", 400
        
        new_uuid = str(uuid.uuid4())
        if User.query.filter_by(unique_user=new_uuid).first():
            new_uuid = str(uuid.uuid4()) # if the uuid already exists, generate a new one
        
        if User.query.filter_by(email=email).first():
            return "Email is already in use", 400
        
        user = User(name=name, unique_user=new_uuid, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return "User added successfully", 201
    
class UserCollection(Resource):

    def get(self):
        users = User.query.all()
        user_list = [{"id": user.id, 
                      "unique_user": user.unique_user, 
                      "name": user.name, 
                      "email": user.email, 
                      "password": user.password} for user in users]
        return user_list, 200
