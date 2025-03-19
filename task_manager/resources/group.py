"""This module contains the resources classes for the Group model."""

import uuid
from flask import request
from flask_restful import Resource
from task_manager.models import Group, User, UserGroup
from task_manager import db

class GroupItem(Resource):
    " Resource class for get, post, put, delete methods for Group"

    # getting group
    def get(self, group_id):
        """Get a group by its ID."""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404
        return {
            "id": group.id,
            "name": group.name,
            "unique_group": group.unique_group
        }, 200

    # creating group
    def post(self):
        "Creates a new group, name and unique uuid is created"  
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        try:
            name = request.json["name"]
            if not isinstance(name, str):
                raise TypeError
        except KeyError:
            return {"error": "Incomplete request - missing name"}, 400
        except TypeError:
            return {"error": "Invalid request - name must be a string"}, 400
        new_uuid = str(uuid.uuid4())
        if Group.query.filter_by(unique_group=new_uuid).first():
            new_uuid = str(uuid.uuid4())

        group = Group(name=name, unique_group=new_uuid)
        db.session.add(group)
        db.session.commit()

        # create usergroup entry for the group
         # Assuming user_id=1 is the admin user
        user_group = UserGroup(user_id=1, group_id=group.id, role="admin")
        db.session.add(user_group)
        db.session.commit()

        response_data = {
            "message": "Group added successfully",
            "group_id": group.id,
            "unique_group": group.unique_group
        }

        return response_data, 201

    # updating group information
    def put(self, group_id):
        """Updates a group information of an existing group"""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        data = request.get_json()
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404
        if "name" in data:
            group.name = data["name"]
        if "unique_group" in data:
            if Group.query.filter_by(unique_group=data["unique_group"]).first():
                return {"error": "unique_group already exists"}, 400
            group.unique_group = data["unique_group"]

        db.session.commit()
        return {
            "message": "Group updated successfully"
        }, 200

    # deleting group
    def delete(self, group_id):
        """Deletes a group by its ID"""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        db.session.delete(group)
        db.session.commit()
        return {"message": "Group deleted successfully"}, 204

class GroupMembers(Resource):
    "Resource class for get method for GroupMembers"
    # getting group members
    def get(self, group_id):
        """Get all members of a group by group ID."""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404
        members = group.user_groups
        return [{
            "id": member.user.id,
            "name": member.user.name,
            "email": member.user.email,
            "role": member.role
        } for member in members], 200

class UserToGroup(Resource):
    "Resource class for post method for UserToGroup"
    # adding user to group
    def post(self, group_id):
        """Add a user to a group."""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        try:
            user_id = request.json["user_id"]
            role = request.json["role"]
        except KeyError:
            return {"error": "Incomplete request - missing fields"}, 400

        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        user = User.query.filter_by(unique_user=user_id).first()
        if not user:
            # debug information - copilot created this line while helping us debug
            print(f"User not found: {user_id}")
            return {"error": "User not found"}, 404

        # debug information - copilot created this line while helping us debug
        print(f"Adding User ID: {user_id} to Group ID: {group_id}")

        if UserGroup.query.filter_by(user_id=user.id, group_id=group_id).first():
            return {"error": "User already in group"}, 400

        user_group = UserGroup(user_id=user.id, group_id=group_id, role=role)
        db.session.add(user_group)
        db.session.commit()

        return {"message": "User added to group successfully"}, 201

    #this is from copilot, wrote just def delete and it suggested this. Approved it.
    def delete(self, group_id):
        """Remove a user from a group."""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        try:
            user_id = request.json["user_id"]
        except KeyError:
            return {"error": "Incomplete request - missing fields"}, 400

        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        user = User.query.filter_by(unique_user=user_id).first()
        if not user:
            return {"error": "User not found"}, 404

        user_group = UserGroup.query.filter_by(user_id=user.id, group_id=group_id).first()
        if not user_group:
            return {"error": "User not in group"}, 400

        db.session.delete(user_group)
        db.session.commit()

        return {"message": "User removed from group successfully"}, 204
