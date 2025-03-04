from flask import request, Response, url_for, jsonify
from flask_restful import Resource
from task_manager.models import Task, Group, UserGroup
from task_manager import db
from datetime import datetime
import uuid

class TaskItem(Resource):

    def get(self):
        pass

    # adding task to group
    def post(self, group_id):
        if not request.is_json:
            return "Request content type must be JSON", 415
        try:
            title = request.json["title"]
            description = request.json["description"]
            status = request.json["status"]
            deadline = datetime.fromisoformat(request.json["deadline"])
            created_at = datetime.fromisoformat(request.json["created_at"])
            updated_at = datetime.fromisoformat(request.json["updated_at"])
        except KeyError:
            return "Incomplete request - missing information", 400
        
        group = Group.query.get(group_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404
        
        user_group = UserGroup.query.filter_by(group_id=group_id).first()
        if not user_group:
            return jsonify({"error": "UserGroup not found for the given group"}), 404
        
        usergroup_id = user_group.id
        new_uuid = str(uuid.uuid4())
        if Task.query.filter_by(unique_task=new_uuid).first():
            new_uuid = str(uuid.uuid4())

        if Task.query.filter_by(title=title, usergroup_id=usergroup_id).first():
            return "Task already exists", 400
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
        return "Task added successfully", 201

    def put(self, task_id):
        if not request.is_json:
            return "Request content type must be JSON", 415
        data = request.get_json()
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        if "title" in data:
            task.title = data["title"]
        if "description" in data:
            task.description = data["description"]
        if "status" in data:
            task.status = data["status"]
        if "deadline" in data:
            try:
                task.deadline = datetime.fromisoformat(data["deadline"])
            except ValueError:
                return jsonify({"error": "Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400

        task.updated_at = datetime.now()
        db.session.commit()
        return jsonify({"message": "Task updated successfully"}), 200
    
class TaskCollection(Resource):

    # getting all tasks 
    def get(self):
        tasks = Task.query.all()
        task_list = [{"id": task.id, 
                      "title": task.title, 
                      "description": task.description, 
                      "status": task.status, 
                      "deadline": task.deadline, 
                      "created_at": task.created_at, 
                      "updated_at": task.updated_at, 
                      "usergroup_id": task.usergroup_id} for task in tasks]
        return task_list, 200

    def post(self):
        pass

class GroupTaskCollection(Resource):

    # getting group tasks
    def get(self, group_id):
        group = Group.query.get(group_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404
        user_groups = UserGroup.query.filter_by(group_id=group_id).all()
        usergroup_ids = [ug.id for ug in user_groups]
        tasks = Task.query.filter(Task.usergroup_id.in_(usergroup_ids)).all()
        return [{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "deadline": task.deadline,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "usergroup_id": task.usergroup_id
        } for task in tasks]
