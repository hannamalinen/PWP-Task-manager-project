from flask import Blueprint
from flask_restful import Api

from task_manager.resources.task import GroupTaskCollection, TaskItem, TaskCollection
from task_manager.resources.user import UserCollection, UserItem
from task_manager.resources.group import GroupItem, GroupMembers, UserToGroup

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# copilot helped a little to generate proper paths for the resources
api.add_resource(UserItem, "/user/", "/user/<string:unique_user>/")
api.add_resource(UserCollection, "/users/") 
api.add_resource(TaskItem, "/group/<int:group_id>/task/", "/task/<int:task_id>/")
api.add_resource(TaskCollection, "/task/")
api.add_resource(GroupItem, "/group/", "/group/<int:group_id>/")
api.add_resource(GroupMembers, "/group/<int:group_id>/members/")
api.add_resource(UserToGroup, "/group/<int:group_id>/user/")
api.add_resource(GroupTaskCollection, "/group/<int:group_id>/tasks/")
