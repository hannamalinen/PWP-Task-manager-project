"This file tests the models"
import tempfile
import os
from datetime import datetime
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy import event

from task_manager import create_app, db
from task_manager.models import User, Group, Task, UserGroup


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    " Set SQLite PRAGMA"
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def db_handle():
    " Create a database handle, no need for client for db testing"
    db_fd, db_fname = tempfile.mkstemp()
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname})

    with app.app_context():
        db.create_all()
        yield db
        db.session.rollback()
        db.drop_all()
        db.session.remove()

    os.close(db_fd)
    os.unlink(db_fname)

# make all the instances
def get_user():
    return User(
        unique_user="unique_user_1",
        name="Test User",
        email="test.user@testuser.com",
        password="testuser"
    )

def get_group():
    return Group(
        name="Test Group",
        unique_group="unique_group_1"
    )

def get_usergroup(unique_user, unique_group):
    #these was suggested from copilot
    user = User.query.filter_by(unique_user=unique_user).first()
    group = Group.query.filter_by(unique_group=unique_group).first()

    if not user:
        raise ValueError("User not found")
    if not group:
        raise ValueError("Group not found")

    return UserGroup(
        user_id=user.id,
        group_id=group.id,
        role="admin"
    )

def get_task(usergroup_id):
    " Get a task instance"
    usergroup = db.session.get(UserGroup, usergroup_id)
    if not usergroup:
        raise ValueError("UserGroup not found")
    return Task(
        unique_task="unique_task_1",
        title="Test Task",
        description="Test Task Description",
        status=1,
        deadline=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        usergroup_id=usergroup.id
    )

def create_instances(db_handle):
    " Create instances of the models"
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    usergroup = get_usergroup(user.unique_user, group.unique_group)
    db_handle.session.add(usergroup)
    db_handle.session.commit()

    task = get_task(usergroup.id)
    db_handle.session.add(task)
    db_handle.session.commit()

# check that everything exists
    assert User.query.count() == 1
    assert Group.query.count() == 1
    assert UserGroup.query.count() == 1
    assert Task.query.count() == 1

    db_user = User.query.first()
    db_group = Group.query.first()
    db_usergroup = UserGroup.query.first()
    db_task = Task.query.first()
    return db_user, db_group, db_usergroup, db_task

def test_user_model(db_handle):
    " Test the user model"
    user = get_user()
    db_handle.session.add(user)
    db_handle.session.commit()

    assert user.id is not None
    assert user.name == "Test User"
    assert user.email == "test.user@testuser.com"
    assert user.password == "testuser"

def test_group_model(db_handle):
    " Test the group model"
    group = get_group()
    db_handle.session.add(group)
    db_handle.session.commit()

    assert group.id is not None
    assert group.name == "Test Group"

def test_user_group_model(db_handle):
    " Test the user group model"
    user = get_user()
    group = get_group()

    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    usergroup = get_usergroup(user.unique_user, group.unique_group)
    db_handle.session.add(usergroup)
    db_handle.session.commit()

    assert usergroup.id is not None
    assert usergroup.user_id == 1
    assert usergroup.group_id == 1
    assert usergroup.role == "admin"

def test_task_model(db_handle):
    " Test the task model"
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    usergroup = get_usergroup(user.unique_user, group.unique_group)
    db_handle.session.add(usergroup)
    db_handle.session.commit()

    task = get_task(usergroup.id)
    db_handle.session.add(task)
    db_handle.session.commit()

    assert task.id is not None
    assert task.title == "Test Task"
    assert task.description == "Test Task Description"
    assert task.status == 1
    assert task.usergroup_id == 1

# test the schemas
# these all was suggested from copilot, when writing test_schema
def test_user_schema(db_handle):
    " Test the user schema"
    user = get_user()
    db_handle.session.add(user)
    db_handle.session.commit()

    assert user.json_schema() == {
        "type": "object",
        "required": ["name", "email", "password"],
        "properties": {
            "name": {
                "description": "Name of the user",
                "type": "string"
            },
            "email": {
                "description": "Email of the user",
                "type": "string"
            },
            "password": {
                "description": "Password of the user",
                "type": "string"
            }
        }
    }
def test_group_schema(db_handle):
    " Test the group schema"
    group = get_group()
    db_handle.session.add(group)
    db_handle.session.commit()

    assert group.json_schema() == {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {
                "description": "Name of the group",
                "type": "string"
            }
        }
    }
def test_user_group_schema(db_handle):
    " Test the user group schema"
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    usergroup = get_usergroup(user.unique_user, group.unique_group)
    db_handle.session.add(usergroup)
    db_handle.session.commit()

    assert usergroup.json_schema() == {
        "type": "object",
        "required": ["role"],
        "properties": {
            "role": {
                "description": "Role of the user in the group",
                "type": "string"
            }
        }
    }
def test_task_schema(db_handle):
    "Test the task schema"
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    usergroup = get_usergroup(user.unique_user, group.unique_group)
    db_handle.session.add(usergroup)
    db_handle.session.commit()

    task = get_task(usergroup.id)
    db_handle.session.add(task)
    db_handle.session.commit()

    assert task.json_schema() == {
        "type": "object",
        "required": ["title", "description", "status", "deadline",
                    "created_at", "updated_at", "usergroup_id"],
        "properties": {
            "title": {
                "description": "Title of the task",
                "type": "string"
            },
            "description": {
                "description": "Description of the task",
                "type": "string"
            },
            "status": {
                "description": "Status of the task",
                "type": "integer"
            },
            "deadline": {
                "description": "Deadline of the task",
                "type": "string",
                "format": "date-time"
            },
            "created_at": {
                "description": "Creation time of the task",
                "type": "string",
                "format": "date-time"
            },
            "updated_at": {
                "description": "Last update time of the task",
                "type": "string",
                "format": "date-time"
            },
            "usergroup_id": {
                "description": "User group ID",
                "type": "integer"
            }
        }
    }

    # test the serialize and deserialize methods
def test_user_serialize_deserialize(db_handle):
    " Test the serialize and deserialize methods for the user model"
    user = get_user()
    db_handle.session.add(user)
    db_handle.session.commit()

    doc = user.serialize()
    assert doc == {
        "name": "Test User",
        "email": "test.user@testuser.com",
        "password": "testuser",
        "unique_user": "unique_user_1"
    }

    # Test deserialize method
    new_user = User()
    new_user.deserialize(doc)
    assert new_user.name == "Test User"
    assert new_user.email == "test.user@testuser.com"
    assert new_user.password == "testuser"
    assert new_user.unique_user == "unique_user_1"

def test_group_serialize_deserialize(db_handle):
    " Test the serialize and deserialize methods for the group model"
    group = get_group()
    db_handle.session.add(group)
    db_handle.session.commit()

    doc = group.serialize()
    assert doc == {
        "name": "Test Group",
    }

    # Test deserialize method
    new_group = Group()
    new_group.deserialize(doc)
    assert new_group.name == "Test Group"

def test_usergroup_serialize_deserialize(db_handle):
    " Test the serialize and deserialize methods for the user group model"
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    usergroup = get_usergroup(user.unique_user, group.unique_group)
    db_handle.session.add(usergroup)
    db_handle.session.commit()

    doc = usergroup.serialize()
    assert doc == {
        "role": "admin"
    }

    # test deserialize method
    new_usergroup = UserGroup()
    new_usergroup.deserialize(doc)
    assert new_usergroup.role == "admin"

#from copilot
def test_task_serialize_deserialize(db_handle):
    " Test the serialize and deserialize methods for the task model"
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    usergroup = get_usergroup(user.unique_user, group.unique_group)
    db_handle.session.add(usergroup)
    db_handle.session.commit()

    task = get_task(usergroup.id)
    db_handle.session.add(task)
    db_handle.session.commit()

    doc = task.serialize()
    assert doc == {
        "title": "Test Task",
        "description": "Test Task Description",
        "status": 1,
        "deadline": task.deadline,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "usergroup_id": task.usergroup_id,
    }

    # test deserialize method
    new_task = Task()
    new_task.deserialize(doc)
    assert new_task.title == "Test Task"
    assert new_task.description == "Test Task Description"
    assert new_task.status == 1
    assert new_task.deadline == task.deadline
    assert new_task.created_at == task.created_at
    assert new_task.updated_at == task.updated_at
    assert new_task.usergroup_id == task.usergroup_id
