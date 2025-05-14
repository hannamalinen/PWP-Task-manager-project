"""This module contains the resources for the Task model."""
import uuid
from datetime import datetime
import requests  # Third-party import
from flask import request
from flask_restful import Resource
from task_manager.models import Task, Group
from task_manager import db

class GroupTaskCollection(Resource):
    """Resource class for get method for GroupTaskCollection"""

    def get(self, group_id):
        """Get all tasks of a group"""
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        # Fetch tasks directly associated with the group
        tasks = Task.query.filter_by(group_id=group_id).all()
        return [{
            "id": task.id,
            "unique_task": task.unique_task,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "deadline": task.deadline.isoformat(),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "group_id": task.group_id
        } for task in tasks], 200

    def post(self, group_id):
        """Creates a new task"""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        try:
            title = request.json["title"]
            description = request.json["description"]
            status = request.json["status"]
            deadline = datetime.fromisoformat(request.json["deadline"])
            created_at = datetime.now()
            updated_at = datetime.now()
        except KeyError:
            return {"error": "Incomplete request - missing information"}, 400

        if not title:
            return {"error": "Title is required"}, 400
        if not description:
            return {"error": "Description is required"}, 400
        if not isinstance(status, int):
            return {"error": "Status must be an integer"}, 400
        if not deadline:
            return {"error": "Deadline is required"}, 400

        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        new_uuid = str(uuid.uuid4())
        if Task.query.filter_by(unique_task=new_uuid).first():
            new_uuid = str(uuid.uuid4())

        if Task.query.filter_by(title=title, group_id=group_id).first():
            return {"error": "Task already exists"}, 400

        task = Task(
            unique_task=new_uuid,
            title=title,
            description=description,
            status=status,
            deadline=deadline,
            created_at=created_at,
            updated_at=updated_at,
            group_id=group_id
        )
        db.session.add(task)
        db.session.commit()

        # Send email notifications (if applicable)
        if status == 1:
            email_data = {
                "recipient": "pvaaraniemi21@student.oulu.fi",
                "subject": f"Task '{title}' is completed!",
                "body": (
                    f"Hello,\n\n"
                    f"The task '{title}' in group {group.name} has been marked as completed.\n\n"
                    f"Best regards,\n"
                    f"Task Manager App"
                )
            }
            try:
                print("Sending email with data:", email_data)  # Debugging statement
                response = requests.post("http://127.0.0.1:8000/api/emails/", json=email_data, timeout=10)
                if response.status_code != 200:
                    print(f"Failed to send completion email: {response.json()}")
            except requests.exceptions.RequestException as exception:
                print(f"Error contacting email service: {str(exception)}")

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
            print(f"Group with ID {group_id} not found")
            return {"error": "Group not found"}, 404

        task = Task.query.filter_by(unique_task=unique_task, group_id=group_id).first()
        if not task:
            print(f"Task with unique_task {unique_task} not found in group {group_id}")
            return {"error": "Task not found"}, 404

        # Return the task details
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "deadline": task.deadline.isoformat(),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "group_id": task.group_id
        }, 200

    def put(self, group_id, unique_task):
        """Updates a task information of an existing task"""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        data = request.get_json()
        group = db.session.get(Group, group_id)
        if not group:
            return {"error": "Group not found"}, 404

        task = Task.query.filter_by(unique_task=unique_task, group_id=group_id).first()
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
                    "recipient": "pvaaraniemi21@student.oulu.fi",
                    "subject": f"Task '{task.title}' is completed!",
                    "body": f"The task '{task.title}' in group {group_id} has been marked as done."
                }
                try:
                    print("Sending email with data:", email_data)  # Debugging statement
                    response = requests.post("http://127.0.0.1:8000/api/emails/", json=email_data, timeout=10)
                    if response.status_code != 200:
                        return {"error": f"Failed to send email: {response.json()}"}, response.status_code
                except requests.exceptions.RequestException as exception:
                    return {"error": f"Failed to connect to email service: {str(exception)}"}, 500

            task.status = data["status"]
        if "deadline" in data:
            try:
                task.deadline = datetime.fromisoformat(data["deadline"])

                # Send email notification for deadline reminder
                now = datetime.now()
                deadline_date = task.deadline.date()
                now_date = now.date()

                days_until_deadline = (deadline_date - now_date).days

                if 0 <= days_until_deadline <= 3:
                    email_data = {
                        "recipient": "pvaaraniemi21@student.oulu.fi",
                        "subject": f"Reminder: Deadline for '{task.title}' is due in {days_until_deadline} day(s)",
                        "body": (
                            f"Hello,\n\n"
                            f"This is a reminder that the task '{task.title}' has a deadline on "
                            f"{task.deadline.strftime('%Y-%m-%d at %H:%M')}.\n"
                            f"You have {days_until_deadline} day(s) left to complete it.\n\n"
                            f"Best regards,\n"
                            f"Task Manager App"
                        )
                    }
                    try:
                        print("Sending email with data:", email_data)  # Debugging statement
                        response = requests.post("http://127.0.0.1:8000/api/emails/", json=email_data, timeout=10)
                        if response.status_code != 200:
                            print(f"Deadline reminder failed: {response.json()}")
                    except requests.exceptions.RequestException as exception:
                        print(f"Error contacting email service: {str(exception)}")
            except ValueError:
                return {"error": "Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400

        task.updated_at = datetime.now()
        db.session.commit()
        return {"message": "Task updated successfully"}, 200

    def delete(self, group_id, unique_task):
        """Deletes a task by its unique_task"""
        group = db.session.get(Group, group_id)
        if not group:
            print(f"Group with ID {group_id} not found")
            return {"error": "Group not found"}, 404

        task = Task.query.filter_by(unique_task=unique_task, group_id=group_id).first()
        if not task:
            print(f"Task with unique_task {unique_task} not found in group {group_id}")
            return {"error": "Task not found"}, 404

        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deleted successfully"}, 204
