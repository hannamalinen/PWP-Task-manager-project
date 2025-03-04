import uuid
import time
import os
import tempfile
import pytest
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers
from task_manager import create_app, db
from task_manager.models import User, Group, ApiKey

TEST_KEY = "tepontarinat"

# from github /tests/resource_test.py
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/tests/resource_test.py
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
        # test valid user creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Teppo Testaaja",
                "email": "teppo.testaaja@gmail.com",
                "password": "teponsalasana123"
            }
        )
        assert resp.status_code == 201  # ok

        # test invalid user creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Teppo Testaaja",
                "password": "teponsalasana123"
            }
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Incomplete request - missing fields"}

        # create valid user for testing delete
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Delete This",
                "email": "delete.this@gmail.com",
                "password": "deletethis123"
            }
        )
        assert resp.status_code == 201  # ok
        user_data = resp.get_json()
        assert user_data is not None
        assert "unique_user" in user_data
        unique_user = user_data["unique_user"]

        # remove user from database
        resp = client.delete(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 204  # user removed
        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 404
        assert resp.get_json() == {'error': 'User not found'}

    def test_updating_user(self, client):
        # create user to update
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Update Me",
                "email": "update.me@gmail.com",
                "password": "updateme123"
            }
        )
        assert resp.status_code == 201  # ok
        user_data = resp.get_json()
        assert user_data is not None
        assert "unique_user" in user_data
        unique_user = user_data["unique_user"]

        # update the user's information
        resp = client.put(
            f"{self.RESOURCE_URL}{unique_user}/",
            json={
                "name": "Updated Name",
                "email": "updated.email@gmail.com",
                "password": "updatedpassword123"
            }
        )
        assert resp.status_code == 200  # ok
        assert resp.get_json() == {"message": "User updated successfully"}

        # update
        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 200
        updated_user_data = resp.get_json()
        assert updated_user_data["name"] == "Updated Name"
        assert updated_user_data["email"] == "updated.email@gmail.com"

    def test_get_user(self, client):
        # create a user to get
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Get User",
                "email": "get.user@gmail.com",
                "password": "getuserpassword"
            }
        )
        assert resp.status_code == 201, f"User creation failed: {resp.get_data(as_text=True)}"
        user_data = resp.get_json()
        unique_user = user_data["unique_user"]

        # test getting the user
        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 200, f"User retrieval failed: {resp.get_data(as_text=True)}"
        retrieved_user = resp.get_json()
        assert retrieved_user["name"] == "Get User"

    def test_get_all_users(self, client):
        # create users to get
        for i in range(3):
            resp = client.post(
                self.RESOURCE_URL,
                json={
                    "name": f"User {i+1}",
                    "email": f"user{i+1}@gmail.com",
                    "password": f"userpassword{i+1}"
                }
            )
            assert resp.status_code == 201, f"User creation failed: {resp.get_data(as_text=True)}"

        # test getting all users
        resp = client.get("/api/users/")
        assert resp.status_code == 200, f"User retrieval failed: {resp.get_data(as_text=True)}"
        users = resp.get_json()
        assert len(users) == 6, "Expected 6 users"
        # Including the initial 3 users created in _populate_db
        # copilot created this thing above to help debug the test

class TestGroup(object):
    RESOURCE_URL = "/api/group/"

    def test_creating_group(self, client):
        # test valid group creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Toimarit"
            }
        )
        assert resp.status_code == 201  # Successful creation

        # test invalid group creation
        resp = client.post(
            self.RESOURCE_URL,
            json={"name": True}
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Invalid request - name must be a string"}

    def test_updating_group(self, client):
        # create group to update
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Update Group",
                "unique_group": "update-group-uuid"
            }
        )
        assert resp.status_code == 201  # ok
        group_data = resp.get_json()
        assert group_data is not None, "Failed to create group"
        assert "group_id" in group_data, "Response does not contain group_id"
        group_id = group_data["group_id"]

        # update the group's information
        resp = client.put(
            f"{self.RESOURCE_URL}{group_id}/",
            json={
                "name": "Updated Group Name",
                "unique_group": "updated-unique-group"
            }
        )
        assert resp.status_code == 200  # ok
        assert resp.get_json() == {"message": "Group updated successfully"}

        # update the group's information
        resp = client.get(f"{self.RESOURCE_URL}{group_id}/")
        assert resp.status_code == 200
        updated_group_data = resp.get_json()
        assert updated_group_data["name"] == "Updated Group Name"
        assert updated_group_data["unique_group"] == "updated-unique-group"

    def test_get_group(self, client):
        # create group for getting
        resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Retrieve Group"}
        )
        assert resp.status_code == 201, f"Group creation failed: {resp.get_data(as_text=True)}"
        group_data = resp.get_json()
        group_id = group_data["group_id"]

        # test getting the group
        resp = client.get(f"{self.RESOURCE_URL}{group_id}/")
        assert resp.status_code == 200, f"Group retrieval failed: {resp.get_data(as_text=True)}"
        retrieved_group = resp.get_json()
        assert retrieved_group["name"] == "Retrieve Group"

    def test_get_group_members(self, client):
        # create a group and add a user to the group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Members Group"}
        )
        resp_message = group_resp.get_data(as_text=True)
        assert group_resp.status_code == 201, f"Group creation failed: {resp_message}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        user_resp = client.post(
            "/api/user/",
            json={
                "name": "Member User",
                "email": "member.user@gmail.com",
                "password": "memberpassword"
            }
        )
        resp_message = group_resp.get_data(as_text=True)
        assert user_resp.status_code == 201, f"User creation failed: {resp_message}"
        user_data = user_resp.get_json()
        resp_user_message = user_resp.get_data(as_text=True)
        user_creation_message = "User creation failed: {resp_user_message}"
        assert "unique_user" in user_data, user_creation_message
        user_id = user_data["unique_user"]

        # add user to the db
        with client.application.app_context():
            db.session.commit()

        # a delay to allow the database to process the commit
        # copilot created this to help debug the test
        time.sleep(1)

        # debug information - copilot created this to help debug the test
        print(f"User ID: {user_id}")

        add_user_resp = client.post(
            f"/api/group/{group_id}/user/",
            json={"user_id": user_id, "role": "member"}
        )
        resp_add_user_message = add_user_resp.get_data(as_text=True)
        assert_message = f"Adding user to group failed: {resp_add_user_message}"
        assert add_user_resp.status_code == 201, assert_message
        # test getting group members
        resp = client.get(f"{self.RESOURCE_URL}{group_id}/members/")
        assert_message = f"Group members retrieval failed: {resp.get_data(as_text=True)}"
        assert resp.status_code == 200, assert_message
        members = resp.get_json()
        # copilot created this to help debug the test
        assert len(members) == 2, "Expected 2 members"
        assert any(member["name"] == "Member User" for member in members)

    def test_add_user_to_group(self, client):
        # create group + user to add to the group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Add User Group"}
        )
        assert_group_message = group_resp.get_data(as_text=True)
        assert group_resp.status_code == 201, f"Group creation failed: {assert_group_message}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        user_resp = client.post(
            "/api/user/",
            json={
                "name": "Add User",
                "email": "add.user@gmail.com",
                "password": "adduserpassword"
            }
        )
        assert_user_message = user_resp.get_data(as_text=True)
        assert user_resp.status_code == 201, f"User creation failed: {assert_user_message}"
        user_data = user_resp.get_json()
        assert_user_data_message = {user_resp.get_data(as_text=True)}
        message = f"User creation failed: {assert_user_data_message}"
        assert "unique_user" in user_data, message
        user_id = user_data["unique_user"]

        # commit the user to the database
        with client.application.app_context():
            db.session.commit()

        # a delay to allow the database to process the commit
        # - copilot created this to help debug the test
        time.sleep(1)

        # debug information  - copilot created this to help debug the test
        print(f"User ID: {user_id}")

        # test adding the user to group
        resp = client.post(
            f"/api/group/{group_id}/user/",
            json={"user_id": user_id, "role": "member"}
        )
        user_id_message = resp.get_data(as_text=True)
        message = f"Adding user to group failed: {user_id_message}"
        assert resp.status_code == 201, message
        assert resp.get_json() == {"message": "User added to group successfully"}

class TestTask(object):
    RESOURCE_URL = "/api/task/"

    def test_create_task(self, client):
        # create group to put the task with
        group_resp = client.post(
            "/api/group/",
            json={"name": "Task Group"}
        )
        task_group_message = group_resp.get_data(as_text=True)
        assert group_resp.status_code == 201, f"Group creation failed: {task_group_message}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # test valid task creation
        resp = client.post(
            f"/api/group/{group_id}/task/",
            json={
                "title": "New Task",
                "description": "Task description",
                "status": "Pending",
                "deadline": "2023-12-31T23:59:59",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        )
        task_creation_message = resp.get_data(as_text=True)
        task_message = f"Task creation failed: {task_creation_message}"
        assert resp.status_code == 201, task_message
        task_data = resp.get_json()
        assert "id" in task_data, "Task creation response does not contain 'id'"

    def test_get_task(self, client):
        # create group + task to get
        group_resp = client.post(
            "/api/group/",
            json={"name": "Task Group"}
        )
        get_task_message = group_resp.get_data(as_text=True)
        message = f"Group creation failed: {get_task_message}"
        assert group_resp.status_code == 201, message
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        task_resp = client.post(
            f"/api/group/{group_id}/task/",
            json={
                "title": "New Task",
                "description": "Task description",
                "status": "Pending",
                "deadline": "2023-12-31T23:59:59",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        )
        create_task_message = task_resp.get_data(as_text=True)
        message = f"Task creation failed: {create_task_message}"
        assert task_resp.status_code == 201, message
        task_data = task_resp.get_json()
        assert "id" in task_data, "Task creation response does not contain 'id'"
        task_id = task_data["id"]

        # test getting the task
        resp = client.get(f"{self.RESOURCE_URL}{task_id}/")
        get_task_message = resp.get_data(as_text=True)
        message = f"Task retrieval failed: {get_task_message}"
        assert resp.status_code == 200, message
        retrieved_task = resp.get_json()
        assert retrieved_task["title"] == "New Task"
        assert retrieved_task["description"] == "Task description"

    def test_update_task(self, client):
        # create group + task to update
        group_resp = client.post(
            "/api/group/",
            json={"name": "Task Group"}
        )
        update_task_message = group_resp.get_data(as_text=True)
        message = f"Group creation failed: {update_task_message}"
        assert group_resp.status_code == 201, message
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        task_resp = client.post(
            f"/api/group/{group_id}/task/",
            json={
                "title": "New Task",
                "description": "Task description",
                "status": "Pending",
                "deadline": "2023-12-31T23:59:59",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        )
        task_creation_message = task_resp.get_data(as_text=True)
        message = f"Task creation failed: {task_creation_message}"
        assert task_resp.status_code == 201, message
        task_data = task_resp.get_json()
        assert "id" in task_data, "Task creation response does not contain 'id'"
        task_id = task_data["id"]

        # test updating the task
        resp = client.put(
            f"{self.RESOURCE_URL}{task_id}/",
            json={
                "title": "Updated Task",
                "description": "Updated description",
                "status": "Completed",
                "deadline": "2023-12-31T23:59:59"
            }
        )
        assert resp.status_code == 200, f"Task update failed: {resp.get_data(as_text=True)}"
        assert resp.get_json() == {"message": "Task updated successfully"}

        # update
        resp = client.get(f"{self.RESOURCE_URL}{task_id}/")
        update_task_message = resp.get_data(as_text=True)
        message = f"Task retrieval failed: {update_task_message}"
        assert resp.status_code == 200, message
        updated_task = resp.get_json()
        assert updated_task["title"] == "Updated Task"
        assert updated_task["description"] == "Updated description"
        assert updated_task["status"] == "Completed"

    def test_get_all_tasks(self, client):
        # create group + tasks to retrieve
        group_resp = client.post(
            "/api/group/",
            json={"name": "Task Group"}
        )
        get_all_tasks_message = group_resp.get_data(as_text=True)
        message = f"Group creation failed: {get_all_tasks_message}"
        assert group_resp.status_code == 201, message
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        for i in range(3):
            task_resp = client.post(
                f"/api/group/{group_id}/task/",
                json={
                    "title": f"Task {i+1}",
                    "description": f"Task {i+1} description",
                    "status": "Pending",
                    "deadline": "2023-12-31T23:59:59",
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            )
            create_task_message = task_resp.get_data(as_text=True)
            message = f"Task creation failed: {create_task_message}"
            assert task_resp.status_code == 201, message

        # test getting all tasks
        resp = client.get(self.RESOURCE_URL)
        get_all_tasks_message = resp.get_data(as_text=True)
        message = f"Task retrieval failed: {get_all_tasks_message}"
        assert resp.status_code == 200, message
        tasks = resp.get_json()
        assert len(tasks) == 3, "Expected 3 tasks"
        # copilot created this thing above to help debug the test

    def test_get_group_tasks(self, client):
        # create group + tasks to get
        group_resp = client.post(
            "/api/group/",
            json={"name": "Task Group"}
        )
        assert_group_message = group_resp.get_data(as_text=True)
        message = f"Group creation failed: {assert_group_message}"
      
        assert group_resp.status_code == 201, message
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        for i in range(3):
            task_resp = client.post(
                f"/api/group/{group_id}/task/",
                json={
                    "title": f"Task {i+1}",
                    "description": f"Task {i+1} description",
                    "status": "Pending",
                    "deadline": "2023-12-31T23:59:59",
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            )
            create_task_message = task_resp.get_data(as_text=True)
            message = f"Task creation failed: {create_task_message}"
            assert task_resp.status_code == 201, message
   
        # test getting tasks for the group
        resp = client.get(f"/api/group/{group_id}/tasks/")
        assert resp.status_code == 200, f"Task retrieval failed: {resp.get_data(as_text=True)}"
        tasks = resp.get_json()
        assert len(tasks) == 3, "Expected 3 tasks"
        # copilot created this thing above to help debug the test
