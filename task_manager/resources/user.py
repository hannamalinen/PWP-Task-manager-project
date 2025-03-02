from flask import request, Response, url_for, jsonify
from flask_restful import Resource
from task_manager.models import User
from task_manager import db
import uuid

class UserItem(Resource):

    def get(self, unique_user):
        user = User.query.filter_by(unique_user=unique_user).first()
        if not user:
            return {"error": "User not found"}, 404

        return {
            "name": user.name,
            "email": user.email,
            "unique_user": user.unique_user
        }, 200

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

        return {
            "message": "User added successfully",
            "unique_user": new_uuid
        }, 201
    
    # deleting a user
    def delete(self, unique_user):
        user = User.query.filter_by(unique_user=unique_user).first()

        if not user:
            return Response("User not found", 404)
        
        db.session.delete(user)
        db.session.commit()

        return Response(status=204)
    
class UserCollection(Resource):

    def get(self):
        users = User.query.all()
        user_list = [{"id": user.id, 
                      "unique_user": user.unique_user, 
                      "name": user.name, 
                      "email": user.email, 
                      "password": user.password} for user in users]
        return user_list, 200
