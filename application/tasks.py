from application.workers import celery
from datetime import datetime
from celery.schedules import crontab
from application.database import db
from application.models import History
import csv
import os

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, just_simple_task.s("hello"), name='add every 10')

@celery.task
def just_simple_task(test):
    print("Just a simple task", test)


@celery.task
def create_history_csv():
    filename = f"history_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    csv_head = ["s.no", "username", "email", "title", "status", "start", "end" ]
    data = []
    with open(os.path.join("./static/exports", filename), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["user", "book", "start", "end"])
        for history in db.session.query(History).all():
            writer.writerow([history.user, history.book, history.start, history.end])
    
    return filename