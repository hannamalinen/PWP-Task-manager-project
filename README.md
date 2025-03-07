# PWP SPRING 2025
# PROJECT NAME Task management API
# Group information
* Student 1. Hanna Malinen hanna.malinen@student.oulu.fi
* Student 2. Petra Vaaraniemi petra.vaaraniemi@student.oulu.fi
* Student 3. Oona Holma oona.holma@student.oulu.fi
* Student 4. Anna Vaara avaara20@student.oulu.fi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

Used database framework: SQLite
sqlite3 version: 2.6.0
python version: 3.12.6

Database/instance/task_management.db <-- our populated database is included in the database

! Requirements included in the Github (requirements.txt) !
Needed requirements:
Flask
Flask-SQLAlchemy
datetime

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

After creating a database, start another terminal and run this command:
flask run
Then we can start with our database and give commands to it! Our HTTP address is 127.0.0.1/5000

![Näyttökuva 2025-02-09 kello 16 00 48](https://github.com/user-attachments/assets/c937b2db-a4ef-4f5b-b46b-7e1b34c7bca0)


## Populating the database
Data can be sent using curl-commands or Postman. We mainly used curl-commands at this point

We only used: POST, GET while testing to populate our database

Few example curl-commands to populate our DB:

- adding a user: curl -X POST http://127.0.0.1:5000/user/add/ -H "Content-Type: application/json" -d "{\"name\": \"John Doe\", \"email\": \"john.doe@example.com\", \"password\": \"password123\"}"

- adding a new task to group: curl -X POST http://127.0.0.1:5000/group/1/task/add/ -H "Content-Type: application/json" -d "{\"title\": \"Complete project\", \"description\": \"Finish the project by end of the week\", \"status\": 1, \"deadline\": \"2025-02-15T00:00:00\", \"created_at\": \"2025-02-01T00:00:00\", \"updated_at\": \"2025-02-01T00:00:00\"}"

## Deployment - COPILOT CREATED INSTRUCTION ON HOW TO DEPLOY OUR API

Prompt for Copilot: Create instructions on how to deploy our Task Management API

To deploy the API, follow these steps:

1. **Set up environment variables**:
    ```sh
    export FLASK_APP=run.py
    export FLASK_ENV=production
    export DATABASE_URL=your_database_url
    ```

2. **Run database migrations**:
    ```sh
    flask db upgrade
    ```

3. **Use Gunicorn to run the application**:
    ```sh
    gunicorn -w 4 -b 0.0.0.0:8000 run:app
    ```

4. **Configure a web server (e.g., Nginx) to proxy requests to Gunicorn**:
    ```nginx
    server {
        listen 80;
        server_name your_domain.com;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

## Running Tests

1. Ensure your virtual environment is activated!

2. Run the tests using pytest:
    ```sh
    pytest tests/api_test.py
    ```
