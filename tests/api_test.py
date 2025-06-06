"""
This module contains the tests for the task manager API. It includes tests for User, Group, and Task resources.
Tests are organized into classes, each focusing on a specific resource. Different resources are tested with valid,
and invalid data and different error cases.

The tests also include creating, updating, deleting, and retrieving users and groups. Same is done to the task resource.
The structure of tests:
- TestUserCollection: Tests for creating and retrieving users, including error cases.
- TestUserItem: Tests for updating, deleting, and retrieving a specific user.
- TestGroupCollection: Tests for creating, updating, deleting, and retrieving groups.
- TestUserToGroup: Tests for adding and removing users from groups.
- TestGroupTaskCollection: Tests for creating and retrieving tasks within groups.
- TestGroupTaskItem: Tests for updating, deleting, and retrieving specific tasks within groups.

"""

import uuid
import time
import os
import tempfile
import pytest
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers
from task_manager import create_app, db
from task_manager.models import User, Group, ApiKey, UserGroup

TEST_KEY = "tepontarinat"

class AuthHeaderClient(FlaskClient):
    """
    A test client that adds the task-manager-api-key header to all requests
    """
    def open(self, *args, **kwargs):
        """
        Add the task-manager-api-key header to all requests
        """
        api_key_headers = Headers({
            'task-manager-api-key': TEST_KEY
        })
        headers = kwargs.pop('headers', Headers())
        headers.extend(api_key_headers)
        kwargs['headers'] = headers
        return super().open(*args, **kwargs)

@pytest.fixture
def client():
    """
    Create a test client for the app
    """
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()

    yield app.test_client()

    with app.app_context():
        db.session.remove()
        db.engine.dispose()
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    """
    Populate the database with test data
    """
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
    # Debug: Print all users in the database
    print("DEBUG: Users in database after _populate_db:")
    for user in User.query.all():
        print(user.serialize())

class TestUserCollection:
    """
    Test the UserCollection resource
    This section includes tests for creating and retrieving the users and test
    different error cases when creating and getting users.
    """
    RESOURCE_URL = "/api/users/"

    def test_creating_user(self, client):
        "Test creating a user with valid and invalid data"

        # Test valid user creation
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123"
            }
        )
        print("Response Data:", resp.get_data(as_text=True))
        assert resp.status_code == 201, f"User creation failed: {resp.get_data(as_text=True)}"
        user_data = resp.get_json()
        assert "unique_user" in user_data, "Response does not contain 'unique_user'"
        assert user_data["message"] == "User added successfully"
        
    def test_getting_users(self, client):
        "Test getting all users from the database"
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200, f"User retrieval failed: {resp.get_data(as_text=True)}"
        users = resp.get_json()
        assert len(users) > 0, "No users found in the database"    

    def test_create_user_with_invalid_data(self, client):
        "test creating user with invalid data and test with missing fields. In this test, the email is missing."
        # Test creating a user with missing fields
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Jane Doe",
                "password": "securepassword123"
            }
        )
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        assert resp.get_json() == {"error": "Incomplete request - missing fields"}

    def test_create_user_with_existing_email(self, client):
        # Create a user
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Duplicate Email User",
                "email": "duplicate.email@gmail.com",
                "password": "password123"
            }
        )
        assert resp.status_code == 201

        # Try creating another user with the same email
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Another User",
                "email": "duplicate.email@gmail.com",
                "password": "password456"
            }
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Email is already in use"}
        
    def test_getting_all_users_when_empty(self, client):
        # Clear the database
        with client.application.app_context():
            db.session.query(User).delete()
            db.session.commit()

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        assert resp.get_json() == []    
        
class TestUserItem:
    "Test the UserItem resource. This includes put, delete, get methods and testing"
    "the faults of the methods"

    RESOURCE_URL = "/api/users/"

    def test_updating_user(self, client):
        "Test updating a user"
        # Create a user
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Update Me",
                "email": "update.me@gmail.com",
                "password": "updateme123"
            }
        )
        assert resp.status_code == 201, f"User creation failed: {resp.get_data(as_text=True)}"
        user_data = resp.get_json()
        assert user_data is not None, "User creation response is empty"
        assert "unique_user" in user_data, "Response does not contain 'unique_user'"
        unique_user = user_data["unique_user"]

        # Debug: Print the unique_user value
        print(f"DEBUG: Unique user ID: {unique_user}")

        # Verify the user exists in the database
        with client.application.app_context():
            user = User.query.filter_by(unique_user=unique_user).first()
            print(f"DEBUG: User found in database: {user.serialize() if user else 'None'}")
            assert user is not None, "User does not exist in the database"

        # Verify the user exists before updating
        print(f"DEBUG: GET request URL: {self.RESOURCE_URL}{unique_user}/")
        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 200, f"User not found before update: {resp.get_data(as_text=True)}"

        # Update the user's information
        resp = client.put(
            f"{self.RESOURCE_URL}{unique_user}/",
            json={
                "name": "Updated Name",
                "email": "updated.email@gmail.com",
                "password": "updatedpassword123"
            }
        )
        assert resp.status_code == 200, f"User update failed: {resp.get_data(as_text=True)}"
        assert resp.get_json() == {"message": "User updated successfully"}

        # Verify the user's information was updated
        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 200, f"User retrieval failed after update: {resp.get_data(as_text=True)}"
        updated_user_data = resp.get_json()
        assert updated_user_data["name"] == "Updated Name", "User name was not updated"
        assert updated_user_data["email"] == "updated.email@gmail.com", "User email was not updated"

    def test_get_user(self, client):
        "test getting user from the database"
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
        "test getting all users from the database"
        for i in range(3):
            resp = client.post(
                self.RESOURCE_URL,
                json={
                    "name": f"User {i+1}",
                    "email": f"user{i+1}@gmail.com",
                    "password": f"userpassword{i+1}"
                }
            )
            print(f"DEBUG: POST /api/users/ response: {resp.get_data(as_text=True)}")
            assert resp.status_code == 201, f"User creation failed: {resp.get_data(as_text=True)}"

        # test getting all users
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200, f"User retrieval failed: {resp.get_data(as_text=True)}"
        users = resp.get_json()
        print(f"DEBUG: Number of users returned: {len(users)}")
        assert len(users) == 6, "Expected 6 users"
        # Including the initial 3 users created in _populate_db
        # copilot created this thing above to help debug the test

    def test_deleting_user(self, client):
        "test deleting user from the database"
        # create user to delete
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Delete User",
                "email": "delete.user@gmail.com",
                "password": "deleteuser123"
            }
        )
        assert resp.status_code == 201  # Successful creation
        user_data = resp.get_json()
        assert user_data is not None
        assert "unique_user" in user_data
        unique_user = user_data["unique_user"]

        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 200, f"User not found before deletion: {resp.get_data(as_text=True)}"

        # delete the user
        resp = client.delete(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 204  # Successful deletion

        # verify the deletion
        resp = client.get(f"{self.RESOURCE_URL}{unique_user}/")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "User not found"}

    def test_deleting_nonexistent_user(self, client):
        "test deleting nonexistent user"
        resp = client.delete(f"{self.RESOURCE_URL}nonexistent_user/")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "User not found"}

    def test_getting_nonexistent_user(self, client):
        resp = client.get(f"{self.RESOURCE_URL}nonexistent-user-id/")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "User not found"}
    
    def test_updating_nonexistent_user(self, client):
        resp = client.put(
            f"{self.RESOURCE_URL}nonexistent-user-id/",
            json={"name": "Updated Name"}
        )
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "User not found"} 

class TestGroupCollection(object):
    "Test the Group resource"
    RESOURCE_URL = "/api/groups/"

    def test_creating_group(self, client):
        "test creating group to the database"
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

    def test_getting_group(self, client):
        "test getting group from the db"
        resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Toimarit"}
        )
        assert resp.status_code == 201, f"Group creation failed: {resp.get_data(as_text=True)}"
        group_data = resp.get_json()
        group_id = group_data["group_id"]

        # test getting the group
        resp = client.get(f"{self.RESOURCE_URL}{group_id}/")
        assert resp.status_code == 200, f"Group retrieval failed: {resp.get_data(as_text=True)}"
        retrieved_group = resp.get_json()
        assert retrieved_group["name"] == "Toimarit"

class TestGroupItem(object):
    "Test the GroupItem resource. This includes put, delete, get methods and testing"
    RESOURCE_URL = "/api/groups/"

    def test_get_all_groups(self, client):
        "test getting all groups from the database"
        for i in range(3):
            resp = client.post(
                self.RESOURCE_URL,
                json={
                    "name": f"Group {i+1}",
                    "unique_group": f"group-uuid-{i+1}"
                }
            )
            assert resp.status_code == 201, f"Group creation failed: {resp.get_data(as_text=True)}"

        # test getting all groups
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200, f"Group retrieval failed: {resp.get_data(as_text=True)}"
        groups = resp.get_json()
        assert len(groups) == 6, "Expected 6 groups"

    def test_updating_group(self, client):
        "test updating group"
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

    def test_deleting_group(self, client):
        "test deleting group from the database"
        # create group to delete
        resp = client.post(
            self.RESOURCE_URL,
            json={
                "name": "Delete Group",
                "unique_group": "delete-group-uuid"
            }
        )
        assert resp.status_code == 201  # Successful creation
        group_data = resp.get_json()
        assert group_data is not None, "Failed to create group"
        assert "group_id" in group_data, "Response does not contain group_id"
        group_id = group_data["group_id"]

        # delete the group
        resp = client.delete(f"{self.RESOURCE_URL}{group_id}/")
        assert resp.status_code == 204  # Successful deletion

        # verify the deletion
        resp = client.get(f"{self.RESOURCE_URL}{group_id}/")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Group not found"}

    def test_create_group_with_invalid_data(self, client):
        "test creating group with invalid data"
        resp = client.post(
            self.RESOURCE_URL,
            json={"name": True}
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Invalid request - name must be a string"}

        # created by copilot, when asked to create new tests for group.py
    def test_create_group_with_missing_name(self, client):
        "test creating group with missing name"
        resp = client.post(
            self.RESOURCE_URL,
            json={}
        )
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Incomplete request - missing name"}
    #created by copilot, when asked to create new tests for group.py
    def test_getting_nonexistent_group(self, client):
        "test getting nonexistent group"
        resp = client.get(f"{self.RESOURCE_URL}101/")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Group not found"}

        #created by copilot, when asked to create new tests for group.py
    def test_deleting_nonexistent_group(self, client):
        "test deleting nonexistent group"
        resp = client.delete(f"{self.RESOURCE_URL}101/")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Group not found"}

    # put tests
    # created by copilot, when asked to create new tests for group.py
    def test_updating_nonexistent_group(self, client):
        "test updating nonexistent group"
        resp = client.put(
            f"{self.RESOURCE_URL}101/",
            json={"name": "Updated Group"}
        )
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Group not found"}


class TestUserToGroup(object):
    """
    Test the UserToGroup resource. This includes adding and removing users from groups.
    """
    RESOURCE_URL = "/api/groups/"

    def test_add_user_to_group(self, client):
        "Test adding a user to a group"
        # Create a group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Add User Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # Create a user
        user_resp = client.post(
            "/api/users/",
            json={
                "name": "Add User",
                "email": "add.user@gmail.com",
                "password": "adduserpassword"
            }
        )
        assert user_resp.status_code == 201, f"User creation failed: {user_resp.get_data(as_text=True)}"
        user_data = user_resp.get_json()
        unique_user = user_data["unique_user"]

        # Add the user to the group
        resp = client.post(
            f"{self.RESOURCE_URL}{group_id}/users/{unique_user}/",
            json={"role": "member"}
        )
        assert resp.status_code == 201, f"Adding user to group failed: {resp.get_data(as_text=True)}"
        assert resp.get_json() == {"message": "User added to group successfully"}

    def test_deleting_user_from_group(self, client):
        "Test deleting a user from a group"
        # Create a group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Delete User Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # Create a user
        user_resp = client.post(
            "/api/users/",
            json={
                "name": "Delete User",
                "email": "delete.user@gmail.com",
                "password": "deleteuserpassword"
            }
        )
        assert user_resp.status_code == 201, f"User creation failed: {user_resp.get_data(as_text=True)}"
        user_data = user_resp.get_json()
        unique_user = user_data["unique_user"]

        # Add the user to the group
        add_resp = client.post(
            f"{self.RESOURCE_URL}{group_id}/users/{unique_user}/",
            json={"role": "member"}
        )
        assert add_resp.status_code == 201, f"Adding user to group failed: {add_resp.get_data(as_text=True)}"

        # Delete the user from the group
        delete_resp = client.delete(f"{self.RESOURCE_URL}{group_id}/users/{unique_user}/")
        assert delete_resp.status_code == 204, f"Deleting user from group failed: {delete_resp.get_data(as_text=True)}"

    def test_adding_user_to_nonexistent_group(self, client):
        "Test adding a user to a nonexistent group"
        # Create a user
        user_resp = client.post(
            "/api/users/",
            json={
                "name": "Nonexistent Group User",
                "email": "nonexistent.group.user@gmail.com",
                "password": "password123"
            }
        )
        assert user_resp.status_code == 201, f"User creation failed: {user_resp.get_data(as_text=True)}"
        user_data = user_resp.get_json()
        unique_user = user_data["unique_user"]

        # Attempt to add the user to a nonexistent group
        resp = client.post(
            f"{self.RESOURCE_URL}999/users/{unique_user}/",
            json={"role": "member"}
        )
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Group not found"}

    def test_adding_nonexistent_user_to_group(self, client):
        "Test adding a nonexistent user to a group"
        # Create a group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Nonexistent User Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # Attempt to add a nonexistent user to the group
        resp = client.post(
            f"{self.RESOURCE_URL}{group_id}/users/nonexistent-user-id/",
            json={"role": "member"}
        )
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "User not found"}

    def test_removing_user_from_nonexistent_group(self, client):
        "Test removing a user from a nonexistent group"
        resp = client.delete(f"{self.RESOURCE_URL}999/users/nonexistent-user-id/")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "Group not found"}

    def test_removing_nonexistent_user_from_group(self, client):
        "Test removing a nonexistent user from a group"
        # Create a group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Remove Nonexistent User Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # Attempt to remove a nonexistent user from the group
        resp = client.delete(f"{self.RESOURCE_URL}{group_id}/users/nonexistent-user-id/")
        assert resp.status_code == 404
        assert resp.get_json() == {"error": "User not found"}

    def test_removing_user_which_is_not_in_group(self, client):
        "Test removing a user which is not in a group"
        # Create a group
        group_resp = client.post(
            self.RESOURCE_URL,
            json={"name": "Remove User Not in Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        # Create a user
        user_resp = client.post(
            "/api/users/",
            json={
                "name": "Not in Group User",
                "email": "not.in.group.user@gmail.com",
                "password": "password123"
            }
        )
        assert user_resp.status_code == 201, f"User creation failed: {user_resp.get_data(as_text=True)}"
        user_data = user_resp.get_json()
        unique_user = user_data["unique_user"]

        # Attempt to remove the user from the group
        resp = client.delete(f"{self.RESOURCE_URL}{group_id}/users/{unique_user}/")
        assert resp.status_code == 400
        assert resp.get_json() == {"error": "User not in group"}

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

class TestGroupTaskItem:
    "Test the GroupTaskItem resource"
    RESOURCE_URL = "/api/groups/"

    def test_get_task(self, client):
        "test getting task from the database"
        group_resp = client.post(
            "/api/groups/",
            json={"name": "Task Group"}
        )
        assert group_resp.status_code == 201, f"Group creation failed: {group_resp.get_data(as_text=True)}"
        group_data = group_resp.get_json()
        group_id = group_data["group_id"]

        task_resp = client.post(
            f"{self.RESOURCE_URL}{group_id}/tasks/",
            json={
                "title": "New Task",
                "description": "Task description",
                "status": 0,
                "deadline": "2023-12-31T23:59:59",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        )
        assert task_resp.status_code == 201, f"Task creation failed: {task_resp.get_data(as_text=True)}"
        task_data = task_resp.get_json()
        unique_task = task_data["unique_task"]

        # test getting the task
        resp = client.get(f"{self.RESOURCE_URL}{group_id}/tasks/{unique_task}/")
        assert resp.status_code == 200, f"Task retrieval failed: {resp.get_data(as_text=True)}"
        retrieved_task = resp.get_json()
        assert retrieved_task["title"] == "New Task"
        assert retrieved_task["description"] == "Task description"


