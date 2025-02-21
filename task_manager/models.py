import click
import hashlib
from flask.cli import with_appcontext
from task_manager import db

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
    unique_task = db.Column(db.String(64), nullable=False, unique=True)
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

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
