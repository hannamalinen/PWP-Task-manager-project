from flask import request, Response, url_for, jsonify
from flask_restful import Resource
from task_manager.models import Group, User, UserGroup
from task_manager import db
import uuid

class GroupItem(Resource):

    def get(self):
        pass

    # creating group
    def post(self):
        if not request.is_json:
            return "Request content type must be JSON", 415
        try:
            name = request.json["name"]
        except KeyError:
            return "Incomplete request - missing name", 400
        new_uuid = str(uuid.uuid4())
        if Group.query.filter_by(unique_group=new_uuid).first():
            new_uuid = str(uuid.uuid4()) # if the uuid already exists, generate a new one

        group = Group(name=name, unique_group=new_uuid)
        db.session.add(group)
        db.session.commit()

        return "Group created successfully", group.id, unique_group, 201


class GroupMembers(Resource):

    # getting group members 
    def get(self, group_id):
        group = Group.query.get(group_id)
        if not group:
            return {"error": "Group not found"}, 404
        members = group.user_groups
        return [{
            "id": member.user.id,
            "name": member.user.name,
            "email": member.user.email,
            "role": member.role
            } for member in members]
    
class UserToGroup(Resource):
    
    # adding user to group
    def post(self, group_id):
        if not request.is_json:
            return "Request content type must be JSON", 415
        try:
            user_id = request.json["user_id"]
            role = request.json["role"]
        except KeyError:
            return "Incomplete request - missing fields", 400
        
        group = Group.query.get(group_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if UserGroup.query.filter_by(user_id=user_id, group_id=group_id).first():
            return jsonify({"error": "User already in group"}), 400

        user_group = UserGroup(user_id=user_id, group_id=group_id, role=role)
        db.session.add(user_group)
        db.session.commit()

        return "User added to group successfully", 201
