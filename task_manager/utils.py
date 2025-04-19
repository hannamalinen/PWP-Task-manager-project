from flask import url_for
from task_manager.constants import *
from task_manager.models import *


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    
    Note that child classes should set the *DELETE_RELATION* to the application
    specific relation name from the application namespace. The IANA standard
    does not define a link relation for deleting something.
    """

    DELETE_RELATION = ""

#region User, this includes user methods
    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.
        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.
        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.
        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.
        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href
        
    def add_control_post(self, ctrl_name, title, href, schema):
        """
        Utility method for adding POST type controls. The control is
        constructed from the method's parameters. Method and encoding are
        fixed to "POST" and "json" respectively.
        
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema
        """
    
        self.add_control(
            ctrl_name,
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_put(self, title, href, schema):
        """
        Utility method for adding PUT type controls. The control is
        constructed from the method's parameters. Control name, method and
        encoding are fixed to "edit", "PUT" and "json" respectively.
        
        : param str href: target URI for the control
        : param str title: human-readable title for the control
        : param dict schema: a dictionary representing a valid JSON schema
        """

        self.add_control(
            "edit",
            href,
            method="PUT",
            encoding="json",
            title=title,
            schema=schema
        )
        
    def add_control_delete(self, title, href):
        """
        Utility method for adding PUT type controls. The control is
        constructed from the method's parameters. Control method is fixed to
        "DELETE", and control's name is read from the class attribute
        *DELETE_RELATION* which needs to be overridden by the child class.

        : param str href: target URI for the control
        : param str title: human-readable title for the control
        """
        
        self.add_control(
            "mumeta:delete",
            href,
            method="DELETE",
            title=title,
        )

def get_user_collection():
    """
    Returns a collection of users with hypermedia controls.
    """
    users = User.query.all()
    response = MasonBuilder({
        "items": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "_links": {
                    "self": {"href": f"/api/users/{unique_user}"}
                }
            }
            for user in users
        ]
    })

    # Add controls for the collection
    response.add_control("self", href=USER_COLLECTION_PATH)
    response.add_control_post(
        "add-user",
        title="Add a new user",
        href="/api/users/",
        schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["name", "email", "password"]
        }
    )
    return response


class RespondBody(MasonBuilder):
    """
    A subclass of MasonBuilder that represents a response body for a
    specific resource. This class is used to build the response body
    for the user resource.
    """

    @staticmethod
    def user_item(user):
        """
        Returns a Mason+JSON response for a single user with hypermedia controls.
        :param user: The user object to include in the response.
        """
        if not user:
            response = RespondBody()
            response.add_error("User not found", "The requested user does not exist.")
            return response, 404

        response = RespondBody({
            "id": user.unique_user,
            "name": user.name,
            "email": user.email
        })

        # Add hypermedia controls for the user item
        response.add_control("self", href=url_for("api.get_user", user_id=user.unique_user, _external=True))
        response.add_control_put(
            title="Edit user details",
            href=url_for("api.get_user", user_id=user.unique_user, _external=True),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["name", "email"]
            }
        )
        response.add_control_delete(
            title="Delete this user",
            href=url_for("api.get_user", user_id=user.unique_user, _external=True)
        )
        return response

    @staticmethod
    def user_collection(users):
        """
        Returns a Mason+JSON response for a collection of users with hypermedia controls.
        :param users: A list of user objects to include in the response.
        """
        response = RespondBody({
            "items": [
                {
                    "id": user.unique_user,  # Use unique_user instead of id
                    "name": user.name,
                    "email": user.email,
                    "_links": {
                        "self": {"href": url_for("api.get_user", user_id=user.unique_user, _external=True)}
                    }
                }
                for user in users
            ]
        })

        # Add hypermedia controls for the user collection
        response.add_control("self", href=url_for("api.get_user_collection", _external=True))
        response.add_control_post(
            "add-user",
            title="Add a new user",
            href=url_for("api.create_user", _external=True),
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["name", "email", "password"]
            }
        )
        return response

