from flask import Blueprint
from flask_restful import Api

from email_service.resources.email import EmailCollection, EmailItem

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# Adding resources to the API
api.add_resource(EmailCollection, "/emails/")
api.add_resource(EmailItem, "/emails/<string:email_id>/")