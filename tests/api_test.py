import uuid
import pytest
import tempfile
import os
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers
from task_manager import create_app, db
from task_manager.models import User, Group, UserGroup, Task, ApiKey

TEST_KEY = "tepontarinat"

# from github /tests/resource_test.py
class AuthHeaderClient(FlaskClient):
    def open(self, *args, **kwargs):
        api_key_headers = Headers({
            'task-manager-api-key': TEST_KEY
        })
        headers = kwargs.pop('headers', Headers())
        headers.extend(api_key_headers)
        kwargs['headers'] = headers
        return super().open(*args, **kwargs)

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()

    #app.test_client_class = AuthHeaderClient
    yield app.test_client()

    with app.app_context():
        db.session.remove()
        db.engine.dispose()
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    for i in range(1, 4):
        user = User(
            unique_user=str(uuid.uuid4()),
            name=f"Test User {i}",
            email=f"testemail{i}@gmail.com",
            password=f"password{i}"
        )
        group = Group(
            name=f"Test Group {i}",
            unique_group=str(uuid.uuid4())
        )
        db.session.add(user)
        db.session.add(group)

    db_key = ApiKey(
        key=ApiKey.key_hash(TEST_KEY),
        admin=True
    )
    db.session.add(db_key)
    db.session.commit()

class TestUser(object):
    RESOURCE_URL = "/api/user/"

    def test_creating_user(self, client):
        # Test valid user creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Teppo Testaaja",
                "email": "teppo.testaaja@gmail.com",
                "password": "teponsalasana123"
            }
        )
        assert resp.status_code == 201  # Successful creation

        # Test invalid user creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Teppo Testaaja",
                "password": "teponsalasana123"
            }
        )
        assert resp.status_code == 400
        assert resp.get_json() == "Incomplete request - missing fields"

        # Create a valid user for deletion test
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Delete This",
                "email": "delete.this@gmail.com",
                "password": "deletethis123"
            }
        )
        assert resp.status_code == 201  # Successful creation
        user_data = resp.get_json()
        assert user_data is not None
        assert "unique_user" in user_data
        unique_user = user_data["unique_user"]

        # Remove user from database
        #unique_user = resp.get_json()["unique_user"]
        resp = client.delete(f"{self.RESOURCE_URL}{unique_user}/") # copilot suggested this
        assert resp.status_code == 204  # The user was removed
        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 404
        assert resp.get_json() == {'error': 'User not found'}

    def test_updating_user(self, client):
        # Create a user to update
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Update Me",
                "email": "update.me@gmail.com",
                "password": "updateme123"
            }
        )
        assert resp.status_code == 201  # Successful creation
        user_data = resp.get_json()
        assert user_data is not None
        assert "unique_user" in user_data
        unique_user = user_data["unique_user"]

        # Update the user's information
        resp = client.put(
            f"{self.RESOURCE_URL}{unique_user}/",
            json={
                "name": "Updated Name",
                "email": "updated.email@gmail.com",
                "password": "updatedpassword123"
            }
        )
        assert resp.status_code == 200  # Successful update
        assert resp.get_json() == {"message": "User updated successfully"}

        # Verify the update
        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 200
        updated_user_data = resp.get_json()
        assert updated_user_data["name"] == "Updated Name"
        assert updated_user_data["email"] == "updated.email@gmail.com"

class TestGroup(object):
    RESOURCE_URL = "/api/group/"

    def test_creating_group(self, client):
        # Test valid group creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Toimarit"
            }
        )
        assert resp.status_code == 201  # Successful creation

        # Test invalid group creation
        resp = client.post(
            self.RESOURCE_URL,
            json={"name": True}
        )
        assert resp.status_code == 400
        assert resp.get_json() == "Invalid request - name must be a string"

    def test_updating_group(self, client):
        # Create a group to update
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Update Group",
                "unique_group": "update-group-uuid"
            }
        )
        assert resp.status_code == 201  # Successful creation
        group_data = resp.get_json()
        assert group_data is not None, "Failed to create group"
        assert "group_id" in group_data, "Response does not contain group_id"
        group_id = group_data["group_id"]

        # Update the group's information
        resp = client.put(
            f"{self.RESOURCE_URL}{group_id}/",
            json={
                "name": "Updated Group Name",
                "unique_group": "updated-unique-group"
            }
        )
        assert resp.status_code == 200  # Successful update
        assert resp.get_json() == {"message": "Group updated successfully"}

        # Verify the update
        resp = client.get(f"{self.RESOURCE_URL}{group_id}/")
        assert resp.status_code == 200
        updated_group_data = resp.get_json()
        assert updated_group_data["name"] == "Updated Group Name"
        assert updated_group_data["unique_group"] == "updated-unique-group"
