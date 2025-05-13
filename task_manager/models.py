"""This module contains the models for the task manager application."""
import hashlib
import click
from flask.cli import with_appcontext
from task_manager import db
import pytest
from datetime import datetime


# from github
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/models.py
class ApiKey(db.Model):
    " ApiKey Model, from github"
    key = db.Column(db.String(32), nullable=False, unique=True, primary_key=True)
    admin =  db.Column(db.Boolean, default=False)

    @staticmethod
    def key_hash(key):
        " Generate a hash for the key"
        return hashlib.sha256(key.encode()).digest()

# models from exercise 1
class User(db.Model):
    " User database model, models from ex. 1"
    id = db.Column(db.Integer, primary_key=True)
    unique_user = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    user_groups = db.relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")

# from Lovelace
    def serialize(self, short_form=False):
        " Serialize the user, from Lovelace"
        doc = {
            "name" : self.name,
        }
        if not short_form:
            doc["email"] = self.email
            doc["password"] = self.password
            doc["unique_user"] = self.unique_user
        return doc

    def deserialize(self, doc):
        " Deserialize the user"
        self.name = doc["name"]
        self.email = doc["email"]
        self.password = doc["password"]
        self.unique_user = doc["unique_user"]

    @staticmethod
    def json_schema():
        " JSON schema for the user"
        schema = {
            "type": "object",
            "required": ["name", "email", "password"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Name of the user",
            "type": "string"
            }
        props["email"] = {
            "description": "Email of the user",
            "type": "string"
            }
        props["password"] = {
            "description": "Password of the user",
            "type": "string"
            }
        return schema

class Task(db.Model):
    " Task database model, models from ex. 1"
    id = db.Column(db.Integer, primary_key=True)
    unique_task = db.Column(db.String(64), nullable=False, unique=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False)
    group_id = db.Column(db.Integer,
                         db.ForeignKey('group.id', ondelete='SET NULL'),
                         nullable=True)
    # ondelete='SET NULL' is used to set the foreign key to NULL when the referenced row is deleted

   # user_group = db.relationship("UserGroup", back_populates="tasks")
    group = db.relationship("Group", back_populates="tasks")

# from Lovelace
    def serialize(self, short_form=False):
        " Serialize the task, from Lovelace"
        doc = {
            "title" : self.title,
            "deadline" : self.deadline,
            "status" : self.status
        }
        if not short_form:
            doc["description"] = self.description
            doc["created_at"] = self.created_at
            doc["updated_at"] = self.updated_at
            doc["usergroup_id"] = self.usergroup_id
        return doc

    def deserialize(self, doc):
        " Deserialize the task"
        self.title = doc["title"]
        self.description = doc["description"]
        self.status = doc["status"]
        self.deadline = doc["deadline"]
        self.created_at = doc["created_at"]
        self.updated_at = doc["updated_at"]
        self.usergroup_id = doc["usergroup_id"]

    @staticmethod
    def json_schema():
        " JSON schema for the task"
        schema = {
            "type": "object",
            "required": ["title",
                        "description",
                        "status",
                        "deadline",
                        "created_at",
                        "updated_at",
                        "usergroup_id"]
        }
        props = schema["properties"] = {}
        props["title"] = {
            "description": "Title of the task",
            "type": "string"
            }
        props["description"] = {
            "description": "Description of the task",
            "type": "string"
            }
        props["status"] = {
            "description": "Status of the task",
            "type": "integer"
            }
        props["deadline"] = {
            "description": "Deadline of the task",
            "type": "string",
            "format": "date-time"
            }
        props["created_at"] = {
            "description": "Creation time of the task",
            "type": "string",
            "format": "date-time"
            }
        props["updated_at"] = {
            "description": "Last update time of the task",
            "type": "string",
            "format": "date-time"
            }
        props["usergroup_id"] = {
            "description": "User group ID",
            "type": "integer"
            }
        return schema

class Group(db.Model):
    """ Group database model, models from ex. 1 """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    unique_group = db.Column(db.String(64), nullable=False, unique=True)

    user_groups = db.relationship("UserGroup",
                                back_populates="groups",
                                cascade="all, delete-orphan")
    tasks = db.relationship("Task", back_populates="group", cascade="all, delete-orphan")

# from Lovelace
    def serialize(self):
        " Serialize the group, from Lovelace"
        return {
            "name": self.name,
        }
    def deserialize(self, doc):
        " Deserialize the group"
        self.name = doc["name"]   

    @staticmethod
    def json_schema():
        " JSON schema for the group"
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Name of the group",
            "type": "string"
            }
        return schema

class UserGroup(db.Model):
    """ UserGroup database model, models from ex. 1 """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # ondelete='CASCADE' is used to delete all the rows in the child
    # table when the referenced row in the parent table is deleted
    group_id = db.Column(db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'), nullable=False)
     # ondelete='CASCADE' is used to delete all the
     # rows in the child table when the referenced row in the parent table is deleted
    role = db.Column(db.String(64), nullable=False)

    user = db.relationship("User", back_populates="user_groups")
    groups = db.relationship("Group", back_populates="user_groups")

# from Lovelace
    def serialize(self):
        " Serialize the usergroup, from Lovelace"
        return {
            "role": self.role,
        }
    def deserialize(self, doc):
        " Deserialize the usergroup"
        self.role = doc["role"]    

    @staticmethod
    def json_schema():
        " JSON schema for the usergroup"
        schema = {
            "type": "object",
            "required": ["role"]
        }
        props = schema["properties"] = {}
        props["role"] = {
            "description": "Role of the user in the group",
            "type": "string"
            }
        return schema

@click.command("init-db")
@with_appcontext
def init_db_command():
    " Create new tables."
    db.create_all()

