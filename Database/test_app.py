import unittest
import json
from app import app, db, User, Group, UserGroup, Task

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create the database and the database table
        db.create_all()

        # Add a sample user
        self.user = User(id=1, unique_user="unique_user_1", name="Test User", email="test@example.com", password="password")
        db.session.add(self.user)
        db.session.commit()

        # Add a sample group
        self.group = Group(id=1, name="Test Group", unique_group="unique_group_1")
        db.session.add(self.group)
        db.session.commit()

        # Add a sample user group
        self.user_group = UserGroup(id=1, user_id=self.user.id, group_id=self.group.id, role="member")
        db.session.add(self.user_group)
        db.session.commit()

    def tearDown(self):
        # Remove the database and the database table
        db.session.remove()
        db.drop_all()

    def test_add_user(self):
        response = self.app.post('/user/add/', data=json.dumps({
            "name": "New User",
            "email": "newuser@example.com",
            "password": "newpassword"
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("User added successfully", str(response.data))

    def test_create_group(self):
        response = self.app.post('/group', data=json.dumps({
            "name": "New Group",
            "unique_group": "unique_group_2"
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("Group created successfully", str(response.data))

    def test_add_user_to_group(self):
        response = self.app.post('/group/1/add/', data=json.dumps({
            "user_id": 1,
            "role": "admin"
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("User added to group successfully", str(response.data))

    def test_get_group_members(self):
        response = self.app.get('/group/1/members')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test User", str(response.data))

    def test_get_group_tasks(self):
        response = self.app.get('/group/1/tasks')
        self.assertEqual(response.status_code, 200)

    def test_add_task(self):
        response = self.app.post('/group/1/task/add/', data=json.dumps({
            "title": "New Task",
            "description": "Task description",
            "status": 1,
            "deadline": "2025-12-31T23:59:59",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("Task added successfully", str(response.data))

    def test_get_tasks(self):
        response = self.app.get('/task/get/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()