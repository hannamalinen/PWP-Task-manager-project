from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task_management.db" ## our database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app) 

# models from exercise 1
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_user = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    user_groups = db.relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_task(db.String(64), nullable=False, unique=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False)
    usergroup_id = db.Column(db.Integer, db.ForeignKey('user_group.id', ondelete='SET NULL'), nullable=False)  # ondelete='SET NULL' is used to set the foreign key to NULL when the referenced row is deleted

    user_group = db.relationship("UserGroup", back_populates="tasks")

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    unique_group = db.Column(db.String(64), nullable=False, unique=True)

    user_groups = db.relationship("UserGroup", back_populates="groups", cascade="all, delete-orphan")

class UserGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)  # ondelete='CASCADE' is used to delete all the rows in the child table when the referenced row in the parent table is deleted
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'), nullable=False)  # ondelete='CASCADE' is used to delete all the rows in the child table when the referenced row in the parent table is deleted
    role = db.Column(db.String(64), nullable=False)
    
    user = db.relationship("User", back_populates="user_groups")
    groups = db.relationship("Group", back_populates="user_groups")
    tasks = db.relationship("Task", back_populates="user_group")


## help from exercise 1

# adding a user
@app.route("/user/add/", methods=["POST"])
def add_user():
    if request.method == "POST":
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

        return jsonify({"message": "User added successfully"}), 201
    
    return "POST method required", 405

# creating group
@app.route('/group', methods=['POST'])
def create_group():
    if request.method == "POST":
        if not request.is_json:
            return "Request content type must be JSON", 415
        try:
            name = request.json["name"]
            unique_group = request.json["unique_group"]
        except KeyError:
            return "Incomplete request - missing name", 400
        new_uuid = str(uuid.uuid4())
        if Group.query.filter_by(unique_group=new_uuid).first():
            new_uuid = str(uuid.uuid4()) # if the uuid already exists, generate a new one

        group = Group(name=name, unique_group=new_uuid)
        db.session.add(group)
        db.session.commit()

        return jsonify({"message": "Group created successfully", "group_id":group.id, "unique_group":unique_group}), 201
    
    return "POST method required", 405

# adding user to group
@app.route("/group/<group_id>/add/", methods=["POST"])
def add_user_to_group(group_id):
    if request.method == "POST":
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

        return jsonify({"message": "User added to group successfully"}), 201
    return "POST method required", 405

# getting group members    
@app.route('/group/<group_id>/members', methods=['GET'])
def get_group_members(group_id):
    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    members = group.user_groups
    return jsonify([{
        "id": member.user.id,
        "name": member.user.name,
        "email": member.user.email,
        "role": member.role
        } for member in members])

# getting group tasks
@app.route('/group/<group_id>/tasks', methods=['GET'])
def get_group_tasks(group_id):
    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Group not found"}), 404
    user_groups = UserGroup.query.filter_by(group_id=group_id).all()
    usergroup_ids = [ug.id for ug in user_groups]
    tasks = Task.query.filter(Task.usergroup_id.in_(usergroup_ids)).all()
    return jsonify([{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "deadline": task.deadline,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "usergroup_id": task.usergroup_id
    } for task in tasks])

# adding task to group
@app.route("/group/<group_id>/task/add/", methods=["POST"])
def add_task(group_id):
    if request.method == "POST":
        if not request.is_json:
            return "Request content type must be JSON", 415
        try:
            title = request.json["title"]
            description = request.json["description"]
            status = request.json["status"]
            deadline = datetime.strptime(request.json["deadline"], '%Y-%m-%dT%H:%M:%S')
            created_at = datetime.strptime(request.json["created_at"], '%Y-%m-%dT%H:%M:%S')
            updated_at = datetime.strptime(request.json["updated_at"], '%Y-%m-%dT%H:%M:%S')
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
        task = Task(unique_task=new_uuid, title=title, description=description, status=status, deadline=deadline, created_at=created_at, updated_at=updated_at, usergroup_id=usergroup_id)
        db.session.add(task)
        db.session.commit()
        return jsonify({"message": "Task added successfully"}), 201
    return "POST method required", 405

# getting all tasks        
@app.route("/task/get/", methods=["GET"])
def get_tasks():
    if request.method == "GET":
        tasks = Task.query.all()
        task_list = [{"id": task.id, "title": task.title, "description": task.description, "status": task.status, "deadline": task.deadline, "created_at": task.created_at, "updated_at": task.updated_at, "usergroup_id": task.usergroup_id} for task in tasks]
        return jsonify(task_list), 200
    return "GET method required", 405
