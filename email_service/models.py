import hashlib
import click
from flask.cli import with_appcontext
from task_manager import db
from task_manager.utils import RespondBody

class Email(db.Model):
    "Email database model"
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(64), nullable=False)
    recipient = db.Column(db.String(64), nullable=False)
    subject = db.Column(db.String(128), nullable=False)
    body = db.Column(db.Text, nullable=False)

    def serialize(self, short_form=False):
        " Serialize the email"
        doc = {
            "sender": self.sender,
            "subject": self.subject,
        }
        if not short_form:
            doc["recipient"] = self.recipient
            doc["body"] = self.body
        return doc
    
    def deserialize(self, doc):
        " Deserialize the email"
        self.sender = doc["sender"]
        self.recipient = doc["recipient"]
        self.subject = doc["subject"]
        self.body = doc["body"]

@click.command("init-db")
@with_appcontext
def init_db_command():
    " Create new tables."
    db.create_all()
