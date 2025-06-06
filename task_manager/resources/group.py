"""This module contains the resources classes for the Group model."""

import uuid
from flask import request
from flask_restful import Resource
from task_manager.models import Group, User, UserGroup, Task
from task_manager import db

class GroupItem(Resource):
    " Resource class for get, put, delete methods for Group"

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
            if not isinstance(data["name"], str):
                return {"error": "Name must be a string"}, 400
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

        # Delete all tasks associated with the group
        Task.query.filter_by(group_id=group_id).delete()

        # Delete the group
        db.session.delete(group)
        db.session.commit()
        return {"message": "Group deleted successfully"}, 204

class GroupCollection(Resource):
    "Resource class for get method for GroupCollection"
    # getting all groups
    def get(self):
        """Get all groups"""
        groups = Group.query.all()
        group_list = [{
            "id": group.id,
            "name": group.name,
            "unique_group": group.unique_group
        } for group in groups]
        return group_list, 200

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


class UserToGroup(Resource):
    "Resource class for post method for UserToGroup"

    def get(self, group_id, unique_user):
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
        } for member in members
        ], 200

    def post(self, group_id, unique_user):
        """Assign a user to a group by unique_user."""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        user = User.query.filter_by(unique_user=unique_user).first()
        if not user:
            return {"error": "User not found"}, 404

        # Check if the user is already in the group
        if UserGroup.query.filter_by(user_id=user.id, group_id=group_id).first():
            return {"error": "User is already in the group"}, 400

        # Add the user to the group
        role = request.json.get("role", "member")  # Default role is "member"
        user_group = UserGroup(user_id=user.id, group_id=group_id, role=role)
        db.session.add(user_group)
        db.session.commit()

        return {"message": "User added to group successfully"}, 201

    def delete(self, group_id, unique_user):
        """Remove a user from a group by unique_user."""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        user = User.query.filter_by(unique_user=unique_user).first()
        if not user:
            return {"error": "User not found"}, 404

        user_group = UserGroup.query.filter_by(user_id=user.id, group_id=group_id).first()
        if not user_group:
            return {"error": "User not in group"}, 400

        db.session.delete(user_group)
        db.session.commit()

        return {"message": "User removed from group successfully"}, 204

    def put(self, group_id, unique_user):
        """Update a user's role in a group by unique_user."""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        user = User.query.filter_by(unique_user=unique_user).first()
        if not user:
            return {"error": "User not found"}, 404

        user_group = UserGroup.query.filter_by(user_id=user.id, group_id=group_id).first()
        if not user_group:
            return {"error": "User not in group"}, 400

        # Update the role
        new_role = request.json.get("role")
        if not new_role:
            return {"error": "Role is required"}, 400

        user_group.role = new_role
        db.session.commit()

        return {"message": "User role updated successfully"}, 200

class GroupUsers(Resource):
    """Resource class for get, post methods for GroupUsers"""
    def get(self, group_id):
        """Get all members of a group by group ID."""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        # Fetch all users in the group
        user_groups = UserGroup.query.filter_by(group_id=group_id).all()
        print(f"User groups for group_id {group_id}: {user_groups}")  # Debug log

        if not user_groups:
            print(f"No users found in group {group_id}")
            return [], 200

        users = []
        for user_group in user_groups:
            if user_group.user:  # Ensure user exists
                users.append({
                    "id": user_group.user.id,
                    "unique_user": user_group.user.unique_user,
                    "name": user_group.user.name,
                    "email": user_group.user.email,
                    "role": user_group.role
                })
            else:
                print(f"Orphaned UserGroup entry found: {user_group}")  # Debug log

        print(f"Users in group {group_id}: {users}")  # Debug log
        return users, 200

    def post(self, group_id):
        """Assign a user to a group."""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        # Get the unique_user and role from the request
        data = request.get_json()
        unique_user = data.get("unique_user")
        role = data.get("role")

        if not unique_user or not role:
            return {"error": "unique_user and role are required"}, 400

        # Check if the user exists
        user = User.query.filter_by(unique_user=unique_user).first()
        if not user:
            return {"error": "User not found"}, 404

        # Check if the user is already in the group
        existing_user_group = UserGroup.query.filter_by(user_id=user.id, group_id=group_id).first()
        if existing_user_group:
            return {"error": "User is already in this group"}, 400

        # Add the user to the group
        new_user_group = UserGroup(user_id=user.id, group_id=group.id, role=role)
        db.session.add(new_user_group)
        db.session.commit()

        return {"message": "User added to group successfully"}, 201
