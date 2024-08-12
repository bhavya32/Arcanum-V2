from application.workers import celery
from datetime import datetime, timedelta
from celery.schedules import crontab
from application.database import db
from application.models import User, Book, Section, Purchase
from application.dbFunctions import getAllHistory, getAllIssued, getTimedHistory, mostReadBook, getAllUsers, getAllBooks, getAllSections, getPreviousMonthRange, getPurchasesFiltered, returnBook
import csv
import os
import smtplib
from email.mime.text import MIMEText

smtpObj = smtplib.SMTP('localhost', 1025)
sender = "system@arcanum.in"

reminder_days = 2

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=0, minute=0, day_of_month=1), monthly_activity.s(), name='monthly activity')
    sender.add_periodic_task(crontab(hour=10, minute=0), return_reminder.s(), name='return reminder')


@celery.task
def monthly_activity():
    f,l = getPreviousMonthRange()
    data = getTimedHistory(f,l)
    ## send email to librarian with monthly report
    receivers = ["librarian@arcanum.in"]
    total_reads = len(data)
    ## find the most read book
    pv = getPurchasesFiltered(f,l)
    most_read, most_read_count = mostReadBook(f,l)
    users_added = User.query.filter(User.created_at >= f).filter(User.created_at <= l).count()
    books_added = Book.query.filter(Book.date_created >= f).filter(User.created_at <= l).count()
    sections_added = Section.query.filter(Section.date_created >= f).filter(Section.date_created <= l).count()

    user_count = len(getAllUsers())
    book_count = len(getAllBooks())
    section_count = len(getAllSections())
    ##highest rated books
    top_five_books = Book.query.order_by(Book.rating.desc()).limit(5).all()
    top_five_books = "\n".join([(str(ind+1) + ". " + i.title) for ind, i in enumerate(top_five_books)])
    month_name = f.strftime("%B")
    text = f"""
Dear Librarian,
Here is the monthly report for the library:

Monthly reads: {total_reads}
Most read book in {month_name}: {most_read.title} with {most_read_count} reads
Sales: ₹{pv}

Users added: {users_added}
Books added: {books_added}
Sections added: {sections_added}

Top five books (all time):
{top_five_books}

Total users: {user_count}
Total books: {book_count}
Total sections: {section_count}

Regards,
Arcanum
    """
    message = MIMEText(text, 'plain')
    message['Subject'] = f"Monthly report: {month_name}"
    message['From'] = sender
    message['To'] = receivers[0]
    smtpObj.sendmail(sender, receivers, message.as_string())


@celery.task
def return_reminder():
    print("Reminder task")
    data = getAllIssued()
    for issued in data:
        remaining_days = (issued[3] - datetime.now()).days + 1
        if remaining_days < 0:
            returnBook(issued[1].id, issued[2].id)
            receivers = [issued[1].email]
            text = f"Dear {issued[1].username},\n\nThis is a notification that the book {issued[2].title} has been auto-returned as it was overdue.\n\nRegards,\nLibrarian"
            message = MIMEText(text, 'plain')
            message['Subject'] = f"Auto-returned: {issued[2].title}"
            message['From'] = sender
            message['To'] = issued[1].email

            smtpObj.sendmail(sender, receivers, message.as_string())
            continue

        if remaining_days <= reminder_days:
                
            receivers = [issued[1].email]
            text = f"Dear {issued[1].username},\n\nThis is a reminder that you have to return the book {issued[2].title} in {remaining_days} days.\n\nRegards,\nLibrarian"
            message = MIMEText(text, 'plain')
            message['Subject'] = f"Reminder: {issued[2].title} due for return"
            message['From'] = sender
            message['To'] = issued[1].email

            smtpObj.sendmail(sender, receivers, message.as_string())

@celery.task
def create_history_csv():
    filename = f"history_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    csv_head = ["s.no", "username", "email", "title", "status", "start", "end" ]
    data = getAllHistory()
    data1 = getAllIssued()
    with open(os.path.join("./static/exports", filename), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_head)
        j = 1
        for history in data:
            writer.writerow([j, history[1].username, history[1].email, history[2].title, "RETURNED", history[0].start, history[0].end])
            j+=1
        for issued in data1:
            writer.writerow([j, issued[1].username, issued[1].email, issued[2].title, "ISSUED", issued[0].start, issued[3]])
            j+=1
    
    return filename