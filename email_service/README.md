# Email Notification Guide
## Set up the Email Service

In order to email service work these values have to be set in your venv:  
```
export EMAIL_ADDRESS=<sender's email>  (preferably gmail)
export EMAIL_PASSWORD=<app password>   (app pasword can be ceated in your gmail account)
```  

Email will be sent from address above.

Then you need to run the email service in the port 8000 since 5000 is used by task manager:
```  
export FLASK_APP=email_service 
flask run --port 8000
```  

Now you should be able to use email service. When you modify deadlines or statuses of the tasks, emails should be sent at the moment in this address: pvaarani21@student.oulu.fi

## Check deadlines
There is also script for checking deadlines and sending notifications check_deadlines.py which can currently be run manually.

You need to be in the project root directory and run this command in bash:
```
python -m task_manager.check_deadlines
```
