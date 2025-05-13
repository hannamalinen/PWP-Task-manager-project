"This file tests the models"
import tempfile
import os
from datetime import datetime
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy import event

from task_manager import create_app, db
from task_manager.models import User, Group, Task, UserGroup

## this file is based on the db_test.py from github
## others are prompted from copilot, mainly after errors and asked why this
## is not working, and then it suggested the correct way to do it
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


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

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
    # Query the database for the user and group
    user = User.query.filter_by(unique_user=unique_user).first()
    group = Group.query.filter_by(unique_group=unique_group).first()

    if not user:
        raise ValueError(f"User with unique_user '{unique_user}' not found")
    if not group:
        raise ValueError(f"Group with unique_group '{unique_group}' not found")

    # Create and return a UserGroup object
    return UserGroup(
        user_id=user.id,
        group_id=group.id,
        role="admin"
    )

def get_task(group_id):
    return Task(
        unique_task="test-task-uuid",
        title="Test Task",
        description="Test Task Description",
        status=1,
        deadline=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        group_id=group_id
    )

def create_instances(db_handle):
    "Create instances of the models"
    # Create and add user and group
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    # Create and add usergroup
    usergroup = get_usergroup(user.unique_user, group.unique_group)
    db_handle.session.add(usergroup)
    db_handle.session.commit()

    # Create and add task
    task = get_task(group.id)
    db_handle.session.add(task)
    db_handle.session.commit()

    # Verify that everything exists
    assert User.query.count() == 1
    assert Group.query.count() == 1
    assert UserGroup.query.count() == 1
    assert Task.query.count() == 1

    return user, group, usergroup, task

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
    "Test the task model"
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    # Create a task
    task = Task(
        unique_task="test-task-uuid",
        title="Test Task",
        description="Test Task Description",
        status=1,
        deadline=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        group_id=group.id
    )
    db_handle.session.add(task)
    db_handle.session.commit()

    # Verify the task was created
    retrieved_task = Task.query.filter_by(unique_task="test-task-uuid").first()
    assert retrieved_task is not None
    assert retrieved_task.title == "Test Task"
    assert retrieved_task.description == "Test Task Description"
    assert retrieved_task.group_id == group.id

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

    # Create a task
    task = Task(
        unique_task="test-task-uuid",
        title="Test Task",
        description="Test Task Description",
        status=1,
        deadline=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        group_id=group.id
    )
    db_handle.session.add(task)
    db_handle.session.commit()

    # Verify the task schema
    retrieved_task = Task.query.filter_by(unique_task="test-task-uuid").first()
    assert retrieved_task is not None
    assert retrieved_task.title == "Test Task"
    assert retrieved_task.description == "Test Task Description"
    assert retrieved_task.group_id == group.id

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
    "Test the serialize and deserialize methods for the task model"
    user = get_user()
    group = get_group()
    db_handle.session.add(user)
    db_handle.session.add(group)
    db_handle.session.commit()

    # Create a task
    task = Task(
        unique_task="test-task-uuid",
        title="Test Task",
        description="Test Task Description",
        status=1,
        deadline=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        group_id=group.id
    )
    db_handle.session.add(task)
    db_handle.session.commit()

    # Serialize the task
    serialized_task = {
        "id": task.id,
        "unique_task": task.unique_task,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "deadline": task.deadline.isoformat(),
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "group_id": task.group_id
    }
    assert task.serialize() == serialized_task

    # Deserialize the task
    deserialized_task = Task.deserialize(serialized_task)
    assert deserialized_task.title == task.title
    assert deserialized_task.description == task.description
    assert deserialized_task.group_id == task.group_id

class TestGroupTaskCollection:
    "Test the GroupTaskCollection resource"
    RESOURCE_URL = "/api/groups/"

    def test_create_task(self, client):
        "Test creating a task in the database"
        # Create a group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Task Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # Test valid task creation
        resp = client.post(
            f"{self.RESOURCE_URL}{group_id}/tasks/",
            json={
                "title": "New Task",
                "description": "Task description",
                "status": 0,
                "deadline": "2025-12-31T23:59:59",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        )
        assert resp.status_code == 201, f"Task creation failed: {resp.get_data(as_text=True)}"
        task_data = resp.get_json()
        assert "unique_task" in task_data, "Task creation response does not contain 'unique_task'"
        assert task_data["message"] == "Task added successfully"

    def test_get_all_tasks(self, client):
        "Test retrieving all tasks from the database"
        # Create a group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Task Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # Create multiple tasks
        for i in range(3):
            task_resp = client.post(
                f"{self.RESOURCE_URL}{group_id}/tasks/",
                json={
                    "title": f"Task {i+1}",
                    "description": f"Task {i+1} description",
                    "status": 0,
                    "deadline": "2025-12-31T23:59:59",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00"
                }
            )
            assert task_resp.status_code == 201, f"Task creation failed: {task_resp.get_data(as_text=True)}"

        # Retrieve all tasks
        resp = client.get(f"{self.RESOURCE_URL}{group_id}/tasks/")
        assert resp.status_code == 200, f"Task retrieval failed: {resp.get_data(as_text=True)}"
        tasks = resp.get_json()
        assert len(tasks) == 3, "Expected 3 tasks"

    def test_create_task_with_missing_fields(self, client):
        "Test creating a task with missing fields"
        # Create a group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Task Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # Test creating a task with missing fields
        resp = client.post(
            f"{self.RESOURCE_URL}{group_id}/tasks/",
            json={
                "title": "New Task",
                "description": "Task description",
                "status": 0,
                "deadline": "2025-12-31T23:59:59"
            }
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Incomplete request - missing information"}

def test_create_group(client):
    "Test creating a group"
    # Create a group
    resp = client.post(
        "/api/groups/",
        json={"name": "Test Group"}
    )
    assert resp.status_code == 201, f"Group creation failed: {resp.get_data(as_text=True)}"
    group_data = resp.get_json()
    assert group_data["message"] == "Group added successfully"
    assert "group_id" in group_data
    assert "unique_group" in group_data

    # Verify the group exists in the database
    group = Group.query.filter_by(id=group_data["group_id"]).first()
    assert group is not None
    assert group.name == "Test Group"
