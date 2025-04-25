"""This module contains the resources for the Task model."""
import os
import uuid
from datetime import datetime
from flask import request
from flask_restful import Resource
from task_manager.models import Task, Group, UserGroup
from task_manager import db
import requests

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
            "unique_task": task.unique_task,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "deadline": task.deadline.isoformat(),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "usergroup_id": task.usergroup_id
        } for task in tasks], 200
        # there was also in LoveLace about isoformat, but copilot helped us to implement it

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
            "unique_task": new_uuid
        }, 201

class GroupTaskItem(Resource):
    """Resource class for get, put, delete methods for Task"""    
    def get(self, group_id, unique_task):
        """Get a task by its unique_task and returns the whole task"""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        user_group = UserGroup.query.filter_by(group_id=group_id).first()
        if not user_group:
            return {"error": "UserGroup not found for the given group"}, 404

        usergroup_id = user_group.id
        task = Task.query.filter_by(unique_task=unique_task, usergroup_id=usergroup_id).first()
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
    def put(self, group_id, unique_task):
        """Updates a task information of an existing task"""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        data = request.get_json()
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        user_group = UserGroup.query.filter_by(group_id=group_id).first()
        if not user_group:
            return {"error": "UserGroup not found for the given group"}, 404

        usergroup_id = user_group.id
        task = Task.query.filter_by(unique_task=unique_task, usergroup_id=usergroup_id).first()
        if not task:
            return {"error": "Task not found"}, 404

        if "title" in data:
            if not isinstance(data["title"], str):
                return {"error": "Title must be a string"}, 400
            task.title = data["title"]
        if "description" in data:
            if not isinstance(data["description"], str):
                return {"error": "Description must be a string"}, 400
            task.description = data["description"]
        if "status" in data:
            if not isinstance(data["status"], int):
                return {"error": "Status must be an integer"}, 400
            # Send email notification if status is changed to 1 (completed)
            if task.status != data["status"] and data["status"] == 1:
                email_data = {
                    "sender": os.getenv("EMAIL_ADDRESS"),
                    "recipient": "pvaarani21@student.oulu.fi",
                    "subject": f"Task '{task.title}' is completed!",
                    "body": f"The task '{task.title}' in group {group_id} has been marked as done."
                }
                try:
                    response = requests.post("http://127.0.0.1:8000/api/emails/", json=email_data)
                    if response.status_code != 200:
                        return {"error": f"Failed to send email: {response.json()}"}, response.status_code
                except requests.exceptions.RequestException as e:
                    return {"error": f"Failed to connect to email service: {str(e)}"}, 500
                    
            task.status = data["status"]
        if "deadline" in data:
            try:
                task.deadline = datetime.fromisoformat(data["deadline"])

                now = datetime.now()
                days_until_deadline = (task.deadline - now).days
                
                if 0 <= days_until_deadline <= 3:
                    email_data = {
                        "sender": os.getenv("EMAIL_ADDRESS"),
                        "recipient": "pvaarani21@student.oulu.fi",
                        "subject": f"Reminder: Deadline for '{task.title}' is due in 3 days",
                        "body": (
                            f"This is a reminder that the task '{task.title}' has a deadline on {task.deadline.date()}.\n"
                            f"Only {days_until_deadline} days left!"
                        )
                    }
                    try:
                        response = requests.post("http://127.0.0.1:8000/api/emails/", json=email_data)
                        if response.status_code != 200:
                            print(f"Deadline reminder failed: {response.json()}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error contacting email service: {str(e)}")
            except ValueError:
                return {"error": "Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400

        task.updated_at = datetime.now()
        db.session.commit()
        return {"message": "Task updated successfully"}, 200

    def delete(self, group_id, unique_task):
        """Deletes a task by its unique_task"""
        # Check if the group exists
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        # Find the user group associated with the group_id
        user_group = UserGroup.query.filter_by(group_id=group_id).first()
        if not user_group:
            return {"error": "UserGroup not found for the given group"}, 404

        # Find the task associated with the unique_task and usergroup_id
        usergroup_id = user_group.id
        task = Task.query.filter_by(unique_task=unique_task, usergroup_id=usergroup_id).first()
        if not task:
            return {"error": "Task not found"}, 404

        # Delete the task
        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deleted successfully"}, 204
