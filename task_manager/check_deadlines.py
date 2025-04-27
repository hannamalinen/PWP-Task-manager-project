# ChatGPT helped to implement this script in order to automate the notification of task deadlines
import os
from datetime import datetime
import requests
from task_manager.models import Task

def check_deadlines_and_notify():
    """Check for tasks with deadlines that are today and notify the user."""
    tasks = Task.query.all()

    if not tasks:
        print("No tasks found.")
        return
    
    for task in tasks:
        try:
            now = datetime.now()
            deadline_date = task.deadline.date()
            now_date = now.date()

            days_until_deadline = (deadline_date - now_date).days

            if 0 <= days_until_deadline <= 3:
                email_data = {
                    "recipient": "pvaarani21@student.oulu.fi",
                    "subject": f"Reminder: Deadline for '{task.title}' is due in {days_until_deadline} day(s)",
                    "body": (
                        f"Hello,\n\n"
                        f"This is a reminder that the task '{task.title}' has a deadline on "
                        f"{task.deadline.strftime('%Y-%m-%d at %H:%M')}.\n"
                        f"You have {days_until_deadline} day(s) left to complete it.\n\n"
                        f"Best regards,\n"
                        f"Task Manager App"
                    )
                }
                try:
                    response = requests.post("http://127.0.0.1:8000/api/emails/", json=email_data)
                    if response.status_code != 200:
                        print(f"Deadline reminder failed: {response.json()}")
                except requests.exceptions.RequestException as e:
                    print(f"Error contacting email service: {str(e)}")
        except ValueError:
            return {"error": "Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}, 400
        
if __name__ == "__main__":
    from task_manager import create_app

    app = create_app()

    with app.app_context():
        check_deadlines_and_notify()