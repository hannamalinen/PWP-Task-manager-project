"""This module contains the resources for the Task model."""
import uuid
from datetime import datetime
from flask import request
from flask_restful import Resource
from task_manager.models import Task, Group, UserGroup
from task_manager import db


class TaskItem(Resource):
    """Resource class for get, post, put, delete methods for Task"""

    def get(self, task_id):
        """Get a task by its ID and returns the whole task"""
        task = db.session.get(Task, task_id)
        if not task:
            return {"error": "Task not found"}, 404
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "deadline": task.deadline.isoformat(),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "usergroup_id": task.usergroup_id
        }, 200

    def post(self, group_id):
        """Creates a new task"""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        try:
            title = request.json["title"]
            description = request.json["description"]
            status = request.json["status"]
            deadline = datetime.fromisoformat(request.json["deadline"])
            created_at = datetime.fromisoformat(request.json["created_at"])
            updated_at = datetime.fromisoformat(request.json["updated_at"])
        except KeyError:
            return {"error": "Incomplete request - missing information"}, 400

        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        user_group = UserGroup.query.filter_by(group_id=group_id).first()
        if not user_group:
            return {"error": "UserGroup not found for the given group"}, 404

        usergroup_id = user_group.id
        new_uuid = str(uuid.uuid4())
        if Task.query.filter_by(unique_task=new_uuid).first():
            new_uuid = str(uuid.uuid4())

        if Task.query.filter_by(title=title, usergroup_id=usergroup_id).first():
            return {"error": "Task already exists"}, 400
        task = Task(
            unique_task=new_uuid,
            title=title,
            description=description,
            status=status,
            deadline=deadline,
            created_at=created_at,
            updated_at=updated_at,
            usergroup_id=usergroup_id
            )
        db.session.add(task)
        db.session.commit()
        return {
            "message": "Task added successfully",
            "id": task.id
        }, 201

    def put(self, task_id):
        """Updates a task information of an existing task"""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        data = request.get_json()
        task = db.session.get(Task, task_id)
        if not task:
            return {"error": "Task not found"}, 404
        if "title" in data:
            task.title = data["title"]
        if "description" in data:
            task.description = data["description"]
        if "status" in data:
            task.status = data["status"]
        invalid_format_message = "Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        if "deadline" in data:
            try:
                task.deadline = datetime.fromisoformat(data["deadline"])
            except ValueError:
                return invalid_format_message, 400
        # copilot helped with isoformat thing - the datetime was not working properly

        task.updated_at = datetime.now()
        db.session.commit()
        return {"message": "Task updated successfully"}, 200

class TaskCollection(Resource):

    """Resource class for get, post methods for Task"""

    def get(self):

        """Get all tasks and returns a list of tasks"""

        tasks = Task.query.all()
        task_list = [{"id": task.id,
                      "title": task.title, 
                      "description": task.description, 
                      "status": task.status, 
                      "deadline": task.deadline.isoformat(), 
                      "created_at": task.created_at.isoformat(), 
                      "updated_at": task.updated_at.isoformat(), 
                      "usergroup_id": task.usergroup_id} for task in tasks]
        return task_list, 200
    # copilot helped with isoformat thing - the datetime was not working properly

    def post(self):

        """Creates a new task"""


class GroupTaskCollection(Resource):

    """Resource class for get method for GroupTaskCollection"""

    def get(self, group_id):

        """Get all tasks of a group"""

        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404
        user_groups = UserGroup.query.filter_by(group_id=group_id).all()
        usergroup_ids = [ug.id for ug in user_groups]
        tasks = Task.query.filter(Task.usergroup_id.in_(usergroup_ids)).all()
        return [{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "deadline": task.deadline.isoformat(),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "usergroup_id": task.usergroup_id
        } for task in tasks], 200
        # copilot helped with isoformat thing - the datetime was not working properly
