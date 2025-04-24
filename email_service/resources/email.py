"""This module contains the resources classes for the Email model."""

from flask import request
from flask_restful import Resource
from email_service.models import Email
from email_service import db
from email_service.notify import send_email_notification

class EmailItem(Resource):

    def get(self, email_id):
        """Get an email by its ID."""
        email = db.session.get(Email, email_id)
        if not email:
            return {"error": "Email not found"}, 404
        return email.serialize(), 200
    
class EmailCollection(Resource):

    def get(self):
        """Get all emails."""
        emails = Email.query.all()
        return [email.serialize(short_form=True) for email in emails], 200

    def post(self):
        """Create a new email."""
        if not request.is_json:
            return {"error": "Request content type must be JSON"}, 415
        data = request.get_json()
        if "sender" not in data or "recipient" not in data or "subject" not in data or "body" not in data:
            return {"error": "Missing required fields"}, 400
        
        email = Email()
        email.deserialize(data)
        db.session.add(email)
        db.session.commit()

        try:
            send_email_notification(data["recipient"], data["subject"], data["body"])
            email.status = "sent"
        except Exception as e:
            email.status = "failed"
            email.error_message = str(e)
        
        return email.serialize(), 201
