from celery import Celery
from datetime import datetime, timedelta
from celery.schedules import crontab
from Models.explanation_model import Explanation  
from Models import db  
from app import mail
from celery.utils.log import get_task_logger
from flask_mail import Message

# Initialize Celery with your Flask app
celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # Replace with your broker URL
    result='redis://localhost:6379/0'   # Replace with your result backend URL
)

# Configure Celery to use UTC timezone (important for scheduling)
celery.conf.timezone = 'Asia/Karachi'

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Define a Celery periodic task that runs at the end of each month
    print("checking last month")
    sender.add_periodic_task(
        crontab(day_of_month='1', hour=0, minute=0),  # This schedules the task for the 1st day of each month
        update_views_last_month.s(),
        name='update-views-last-month'
    )

@celery.task
def update_views_last_month():
    # Get the current date
    today = datetime.utcnow().date()
    
    # Check if today is the 1st day of the month
    if today.day == 1:
        # Calculate the date range for the previous month
        last_month_start = today.replace(day=1) - timedelta(days=1)
        last_month_end = today.replace(day=1) - timedelta(days=1, seconds=1)
        
        # Update ViewsLastMonth for relevant records in the Explanation model
        explanations = Explanation.query.filter(
            Explanation.PublishDate >= last_month_start,
            Explanation.PublishDate <= last_month_end
        ).all()

        for explanation in explanations:
            explanation.ViewsLastMonth = explanation.ViewsThisMonth
            explanation.ViewsThisMonth = 0
        print("Last Month Updated")
        # Commit changes to the database
        db.session.commit()



logger = get_task_logger(__name__)
@celery.task
def send_email(subject, sender, recipients, html_body):
    print("\n in send_mail function")
    try:
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.html = html_body
        mail.send(msg)
        print("message sent")
        logger.info(f"Email sent to {recipients}")
    except Exception as e:
        print("error in sending email \n")
        logger.error(f"Error sending email: {str(e)}")