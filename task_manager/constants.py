API_NAME = "task_manager"
MASON = "application/vnd.mason+json"

#Copilot suggested these constants when asked suitable options for our api
# Paths for the API resources
API_PATH = "/api/"
USER_PATH = "/users/"
GROUP_PATH = "/groups/"
TASK_PATH = "/tasks/"

#Specific Resource Paths
USER_COLLECTION_PATH = USER_PATH + "users/"
USER_ITEM_PATH = USER_PATH + "<string:unique_user>/"
GROUP_COLLECTION_PATH = GROUP_PATH + "groups/"
GROUP_ITEM_PATH = GROUP_PATH + "<int:group_id>/"
USER_TO_GROUP_PATH = GROUP_PATH + "<int:group_id>/user/"
GROUP_TASK_COLLECTION_PATH = GROUP_PATH + "<int:group_id>/tasks/"
GROUP_TASK_ITEM_PATH = GROUP_PATH + "<int:group_id>/tasks/<string:unique_task>/"
