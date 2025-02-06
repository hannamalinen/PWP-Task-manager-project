from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task_management.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    tasks = db.relationship("Task", back_populates="user")
    user_groups = db.relationship("UserGroup", back_populates="user")

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    usergroup_id = db.Column(db.Integer, db.ForeignKey('usergroup.id'), nullable=False)

    user = db.relationship("User", back_populates="tasks")
    user_group = db.relationship("UserGroup", back_populates="task")

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    user_groups = db.relationship("UserGroup", back_populates="groups")

class UserGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)

    user = db.relationship("User", back_populates="user_groups")
    groups = db.relationship("Group", back_populates="user_groups")
    tasks = db.relationship("Task", back_populates="user_group")

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
        except ValueError:
            return "Weight and price must be numbers", 400 
        
        if User.query.filter_by(email=email).first():
            return "Email already exists", 400
        
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User added successfully"}), 201
    
    return "POST method required", 405

@app.route('/group', methods=['POST'])
def create_group():
    if request.method == "POST":
        if not request.is_json:
            return "Request content type must be JSON", 415
        try:
            name = request.json["name"]
        except KeyError:
            return "Incomplete request - missing name", 400

        group = Group(name=name)
        db.session.add(group)
        db.session.commit()

        return jsonify({"message": "Group created successfully", "group_id": group.id}), 201
    
    return "POST method required", 405


@app.route("/group/<user>/add/", methods=["POST"])
def add_user_to_group(group_id):
    if request.method == "POST":
        if not request.is_json:
            return "Request content type must be JSON", 415
        try:
            user_id = request.json["user_id"]
        except KeyError:
            return "Incomplete request - missing user_id", 400
        
        group = Group.query.get(group_id)
        if not group:
            return jsonify({"error": "Group not found"}), 404

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if UserGroup.query.filter_by(user_id=user_id, group_id=group_id).first():
            return jsonify({"error": "User already in group"}), 400

        user_group = UserGroup(user_id=user_id, group_id=group_id)
        db.session.add(user_group)
        db.session.commit()

        return jsonify({"message": "User added to group successfully"}), 201
