" This module contains the API resources for the task manager application. "
from flask import Blueprint
from flask_restful import Api

from task_manager.resources.task import GroupTaskCollection, GroupTaskItem
from task_manager.resources.user import UserCollection, UserItem
from task_manager.resources.group import GroupItem, GroupCollection, GroupMembers, UserToGroup

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# copilot helped a little to generate proper paths for the resources
api.add_resource(UserCollection, "/users/")
api.add_resource(UserItem, "/users/<string:unique_user>/")
api.add_resource(GroupCollection, "/groups/")
api.add_resource(GroupItem, "/groups/<int:group_id>/")
api.add_resource(GroupMembers, "/groups/<int:group_id>/members/") # for group members
api.add_resource(UserToGroup, "/groups/<int:group_id>/user/")
api.add_resource(GroupTaskCollection, "/groups/<int:group_id>/tasks/")
api.add_resource(GroupTaskItem, "/groups/<int:group_id>/tasks/<string:unique_task>/")