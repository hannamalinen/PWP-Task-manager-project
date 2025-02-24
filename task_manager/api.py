from flask import Blueprint
from flask_restful import Api

from task_manager.resources.task import TaskItem, TaskCollection
from task_manager.resources.user import UserItem
from task_manager.resources.group import GroupItem, GroupMembers, UserToGroup

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(UserItem, "/user/")
api.add_resource(TaskItem, "/task/<group_id:group_id>/")
api.add_resource(TaskCollection, "/task/")
api.add_resource(GroupItem, "/group/")
api.add_resource(GroupMembers, "/group/<group_id>/members/")
api.add_resource(UserToGroup, "/group/<group_id>/user/")
