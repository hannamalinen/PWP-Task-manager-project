import pytest
from flask import Flask
from task_manager import db
from task_manager.models import User, Group, Task

@pytest.fixture(scope='module')
def test_client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_user_group_relationship(test_client):
    # Create a user
    user = User(unique_user='user1', name='User One', email='user1@example.com', password='password')
    db.session.add(user)
    db.session.commit()

    # Create a group
    group = Group(name='Group One', unique_group='group1')
    db.session.add(group)
    db.session.commit()

    # Associate user with group
    user.groups.append(group)
    db.session.commit()

    # Verify the association
    assert user.groups[0].name == 'Group One'
    assert group.users[0].name == 'User One'

def test_task_group_relationship(test_client):
    # Create a user
    user = User(unique_user='user2', name='User Two', email='user2@example.com', password='password')
    db.session.add(user)
    db.session.commit()

    # Create a group
    group = Group(name='Group Two', unique_group='group2')
    db.session.add(group)
    db.session.commit()

    # Associate user with group
    user.groups.append(group)
    db.session.commit()

    # Create a task
    task = Task(unique_task='task1', title='Task One', description='Description of Task One', status=1, usergroup_id=group.id)
    db.session.add(task)
    db.session.commit()

    # Verify the association
    assert task.user_group.name == 'Group Two'
    assert group.tasks[0].title == 'Task One'