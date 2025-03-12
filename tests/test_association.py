import pytest
from flask import Flask
from task_manager import create_app, db
from task_manager.models import User, Group, user_group_association

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_create_user_and_group(app):
    with app.app_context():
        user = User(unique_user="user1", name="Test User", email="testuser@example.com", password="password")
        group = Group(name="Test Group", unique_group="group1")
        db.session.add(user)
        db.session.add(group)
        db.session.commit()

        assert User.query.count() == 1
        assert Group.query.count() == 1

def test_add_user_to_group(app):
    with app.app_context():
        user = User(unique_user="user1", name="Test User", email="testuser@example.com", password="password")
        group = Group(name="Test Group", unique_group="group1")
        db.session.add(user)
        db.session.add(group)
        db.session.commit()

        stmt = user_group_association.insert().values(user_id=user.id, group_id=group.id, role="member")
        db.session.execute(stmt)
        db.session.commit()

        user_in_group = db.session.query(user_group_association).filter_by(user_id=user.id, group_id=group.id).first()
        assert user_in_group is not None
        assert user_in_group.role == "member"

def test_remove_user_from_group(app):
    with app.app_context():
        user = User(unique_user="user1", name="Test User", email="testuser@example.com", password="password")
        group = Group(name="Test Group", unique_group="group1")
        db.session.add(user)
        db.session.add(group)
        db.session.commit()

        stmt = user_group_association.insert().values(user_id=user.id, group_id=group.id, role="member")
        db.session.execute(stmt)
        db.session.commit()

        user_in_group = db.session.query(user_group_association).filter_by(user_id=user.id, group_id=group.id).first()
        assert user_in_group is not None

        db.session.delete(user_in_group)
        db.session.commit()

        user_in_group = db.session.query(user_group_association).filter_by(user_id=user.id, group_id=group.id).first()
        assert user_in_group is None