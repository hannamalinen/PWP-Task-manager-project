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

        # Remove user from database
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204  # The user was removed
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        assert resp.get_json() == "User not found"

class TestGroup(object):
    RESOURCE_URL = "/api/group/"

    def test_creating_group(self, client):
        # Test valid group creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Toimarit",               
                "unique_group": "toimarit"
            }
        )
        assert resp.status_code == 201  # Successful creation

        # Test invalid group creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": ""
            }
        )
        assert resp.status_code == 400
        assert resp.get_json() == "Incomplete request - missing field"


