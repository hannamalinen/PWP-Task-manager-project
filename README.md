# PWP SPRING 2025
# PROJECT NAME Task management API
# Group information
* Student 1. Hanna Malinen hanna.malinen@student.oulu.fi
* Student 2. Petra Vaaraniemi petra.vaaraniemi@student.oulu.fi
* Student 3. Oona Holma oona.holma@student.oulu.fi
* Student 4. Anna Vaara avaara20@student.oulu.fi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

Used database framework: SQLite
Database/instance/task_management.db <-- our populated database

Requirements included in the Github (requirements.txt)


Remember to activate your virtual environment with these commands:
In all steps, check if you are in the right directory!
cd Database

## creating a virtual environment
Mac:
python3 -m venv myenv

Windows:
python -m venv myenv

## activating the virtual environment
Mac:
source myenv/bin/activate

Windows:
myenv\Scripts\activate

## Install the dependencies
pip install -r requirements.txt

## Creating the database
Go to python console with command:
python

After entering the python console, you can give these commands to create a database:
from app import db
from app import app
ctx = app.app_context()
ctx.push()
db.create_all()
ctx.pop()

In another terminal:
flask run

![Näyttökuva 2025-02-09 kello 16 00 48](https://github.com/user-attachments/assets/c937b2db-a4ef-4f5b-b46b-7e1b34c7bca0)


## Populating the database
Data can be sent using curl-commands or Postman. We mainly used curl-commands at this point

Using SQLite: 
POST, GET

## User-related commands
## Adding new user (name, email, password)
curl -X POST http://127.0.0.1:5000/user/add/ -H "Content-Type: application/json" -d '{"name": "Jane Smith", "email": "jane.smith@example.com", "password": "password123"}'

## UserGroup-related commands
## Adding new user to a group (group number)
curl -X POST http://127.0.0.1:5000/group/1/add/ -H "Content-Type: application/json" -d "{"user_id": 1}"
## Getting the groups designated tasks
curl -X GET http://127.0.0.1:5000/group/1/tasks

## Group-related commands
## Adding new group
curl -X POST http://127.0.0.1:5000/group -H "Content-Type: application/json" -d "{"name": "Developers"}"
To check members of the group
curl -X GET http://127.0.0.1:5000/group/1/members

## Task-related commands
## Getting all tasks
curl -X GET http://127.0.0.1:5000/task/get/

##Adding a new task
curl -X POST http://127.0.0.1:5000/group/1/task/add/ -H "Content-Type: application/json" -d "{"title": "Complete project", "description": "Finish the project by end of the week", "status": 1, "deadline": "2025-02-15T00:00:00", "created_at": "2025-02-01T00:00:00", "updated_at": "2025-02-01T00:00:00"}"

