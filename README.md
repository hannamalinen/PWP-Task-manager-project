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

! Requirements included in requirements.txt !

Remember to activate your virtual environment with these commands:
In all steps, check if you are in the right directory!

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

## RUNNING THE FLASK APP
export FLASK_APP=task_manager
flask run
-> Running on http://127.0.0.1:5000

## STARTING THE EMAIL SERVICE
export EMAIL_SERVICE=anna.vaara.2@gmail.com
export EMAIL_PASSWORD=yryw kjaq eagy khzf

export FLASK_APP=email_service 
flask run --port 8000
-> * Running on http://127.0.0.1:8000

## STARTING THE CLIENT
cd client
npm start
## Creating the database


If wanted to test manually, these commands are needed:

export FLASK_APP=task_manager  
flask init-db  
After creating a database, start another terminal and run this command:  
flask run  
Then we can start with our database and give commands to it! Our HTTP address is 127.0.0.1/5000  

![Näyttökuva 2025-02-09 kello 16 00 48](https://github.com/user-attachments/assets/c937b2db-a4ef-4f5b-b46b-7e1b34c7bca0)

# Removing the database
This is needed when testing endpoints manually.  
source venv/bin/activate  
rm instance/task_management.db  

## Populating the database
Data can be sent using curl-commands or Postman. We mainly used curl-commands at this point

We only used: POST, GET while testing to populate our database

Few example curl-commands to populate our DB:

- adding a user: curl -X POST http://127.0.0.1:5000/user/add/ -H "Content-Type: application/json" -d "{\"name\": \"John Doe\", \"email\": \"john.doe@example.com\", \"password\": \"password123\"}"

- adding a new task to group: curl -X POST http://127.0.0.1:5000/group/1/task/add/ -H "Content-Type: application/json" -d "{\"title\": \"Complete project\", \"description\": \"Finish the project by end of the week\", \"status\": 1, \"deadline\": \"2025-02-15T00:00:00\", \"created_at\": \"2025-02-01T00:00:00\", \"updated_at\": \"2025-02-01T00:00:00\"}"

## Running Tests

1. Ensure your virtual environment is activated!

2. Run the tests using pytest:
    ```sh
    pytest tests/api_test.py
    ```
# Starting the client
First the flask app needs to be running, this is instructed above. After that:
cd client
npm start
Now the client is running in localhost:3000!
