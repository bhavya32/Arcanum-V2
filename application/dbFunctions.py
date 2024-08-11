import io
import datetime
import re
from .models import Author, Authorship, Book, History, Issued, Rating, Request, Section_content, User, Section, db, Policy, Purchase, Comment
from sqlalchemy import func, desc,asc

from matplotlib import pyplot as plt
import numpy as np
from textwrap import wrap
import math
import matplotlib
matplotlib.use('agg')

def deleteComment(id):
    c = Comment.query.filter_by(id=id).first()
    db.session.delete(c)
    db.session.commit()

def createComment(uid, bid, comment):
    c = Comment()
    c.user_id = uid
    c.book_id = bid
    c.content = comment
    db.session.add(c)
    db.session.commit()
    return c

def getComment(uid, bid):
    return Comment.query.filter_by(user_id=uid, book_id=bid).first()
    
def getComments(bid):
    comments = []
    for i in Comment.query.filter_by(book_id=bid).all():
        comment = {}
        comment['content'] = i.content
        comment['user'] = User.query.filter_by(id=i.user_id).first().username
        comment['date'] = i.created_at
        comment['id'] = i.id
        rating = Rating.query.filter_by(user=i.user_id, book=bid).first()
        if rating:
            comment['rating'] = rating.score
        comments.append(comment)
    return comments

def purchaseHistory(start, end):
    #sqlq = r"SELECT strftime('%Y-%m-%d', created_at) AS daily,SUM(value) AS total_value FROM purchase WHERE status = 1 GROUP BY daily ORDER BY daily;"
    sqlq = f"WITH calendar AS (SELECT DATE('{start}') AS date UNION ALL SELECT DATE(date, '+1 day') FROM calendar WHERE date < DATE('{end}')) SELECT c.date AS day, COALESCE(SUM(p.value), 0) AS total_value FROM calendar c LEFT JOIN (select * from purchase where status = 1) p ON DATE(p.created_at) = c.date GROUP BY c.date ORDER BY c.date;"
    r = db.session.execute(db.text(sqlq))
    labels = []
    data = []
    for i in r:
        data.append(i[1])
        labels.append(i[0])
    return [labels, data]

def getPurchasesFiltered(f,l):
    p = Purchase.query.filter(Purchase.created_at >= f).filter(Purchase.created_at <= l).filter(Purchase.status ==1)
    v= p.with_entities(func.sum(Purchase.value)).scalar()
    return v


def getPurchases(uid):
    return Purchase.query.filter_by(user_id=uid, status=1).all()

def checkPurchase(uid, bid):
    print(uid, bid)
    x = Purchase.query.filter_by(user_id=uid, book_id=bid, status=1).first()
    if x:
        return True
    return False

def createPurchase(uid, bid, value):
    p = Purchase()
    p.user_id = uid
    p.book_id = bid
    p.status = 0
    p.value = value
    db.session.add(p)
    db.session.commit()
    return p.id

def setRazID(id, raz_id):
    p = Purchase.query.filter_by(id=id).first()
    p.raz_id = raz_id
    db.session.commit()

def completePurchase(id):
    p = Purchase.query.filter_by(raz_id=id).first()
    p.status = 1
    db.session.commit()

def maxIssueBooks():
    return Policy.query.filter_by(name="MaxBorrowBooks").first().value

def maxBorrowTime():
    return Policy.query.filter_by(name="MaxBorrowDays").first().value

def AutoApprove():
    return Policy.query.filter_by(name="AutoApprove").first().value

def checkAA(uid, bid):
    if AutoApprove() == 1:
        approveRequest(uid, bid)

def updatePolicy(n, v):
    i = Policy.query.filter_by(name=n).first()
    i.value = v
    db.session.commit()
def createUser(fname, lname, username, password, email):
    u = User()
    u.username = username
    u.fname = fname
    u.lname = lname
    u.password = password
    u.email = email
    db.session.add(u)
    db.session.commit()
    return u
def updateInfo(id, fname, lname, email, password):
    u = User.query.filter_by(id=id).first()
    u.fname = fname
    u.lname = lname
    u.email = email
    u.password = password
    db.session.commit()
    return u

def deleteAuthors(bid):
    for auth in Authorship.query.filter_by(book_id=bid).all():
        db.session.delete(auth)
        if len(Authorship.query.filter_by(author_id=auth.author_id).all()) == 0:
            db.session.delete(Author.query.filter_by(id=auth.author_id).first())
    db.session.commit()


def deleteUser(id):
    u = User.query.filter_by(id=id).first()
    
    ##delete all user data
    
    for i in Issued.query.filter_by(user=id).all():
        db.session.delete(i)
    
    for req in Request.query.filter_by(user=id).all():
        db.session.delete(req)
    
    for his in History.query.filter_by(user=id).all():
        db.session.delete(his)
    
    for r in Rating.query.filter_by(user=id).all():
        bid = r.book
        db.session.delete(r)
        updateStaticRating(bid)
        updateTotalReads(bid)
        
    for p in Purchase.query.filter_by(user_id=id).all():
        db.session.delete(p)

    for c in Comment.query.filter_by(user_id=id).all():
        db.session.delete(c)
    db.session.delete(u)
    db.session.commit()


def getUser(username):
    return User.query.filter_by(username=username).first()

def getUserByID(id):
    return User.query.filter_by(id=id).first()


def getRequestStatus(uid, bid):
    return Request.query.filter_by(user=uid, book=bid).first()

def createRequest(uid, bid):
    cr = len(Request.query.filter_by(user=uid).all())
    issued = len(Issued.query.filter_by(user=uid).all())
    #print((cr +issued), maxIssueBooks())
    if (cr +issued)>= maxIssueBooks():
        raise Exception()
    req = Request()
    req.book = bid
    req.user = uid
    db.session.add(req)
    db.session.commit()

##Calculate avg rating
def updateStaticRating(bid):
    avg = Rating.query.with_entities(func.avg(Rating.score).label('average')).filter(Rating.book==bid).first().average
    book = Book.query.filter_by(id=bid).first()
    if avg is None:
        avg=0
    book.rating = round(avg,2)
    db.session.commit()

def updateRating(uid, bid, score):
    rating = Rating.query.filter_by(user=uid, book=bid).first()
    if rating:
        rating.score=score
    else:
        rating = Rating()
        rating.user = uid
        rating.book = bid
        rating.score = score
        db.session.add(rating)
    db.session.commit()
    updateStaticRating(bid)


def fetchRating(uid, bid):
    return Rating.query.filter_by(user=uid, book=bid).first()
    

def fetchAllRatings(bid):
    ratings = Rating.query.filter_by(book=bid).all()
    for i in range(len(ratings)):
        ratings[i].user = User.query.filter_by(id=ratings[i].user).first().username
    return ratings


def updateTotalReads(bid):
    r = len(History.query.filter_by(book=bid).all())
    i = Book.query.filter_by(id=bid).first()
    i.reads=r
    db.session.commit()


def returnBook(uid, bid):
    ##remove from issued and add to history
    i = Issued.query.filter_by(book=bid, user=uid).first()
    h = History()
    h.user = uid
    h.book = bid
    h.start = i.start

    db.session.add(h)
    db.session.delete(i)
    db.session.commit()
    updateTotalReads(bid)
    


def checkIssued(uid, bid):
    for i in getIssued(uid):
        if i.book==bid:
            return True
    return False

def getIssued(id):
    max= maxBorrowTime()
    s = Issued.query.filter_by(user=id).all()
    r = []
    for i in s:
        #Todo 
        ##check if issue is greater than max time
        ## if so, remove
        delta = datetime.date.today() - i.start.date()
        if delta.days > max:
            returnBook(id, i.book)
        else:
            r.append(i)
    return r

def getPastIssued(id):
    s = History.query.filter_by(user=id).order_by(desc(History.end)).all()
    r = []
    for i in s:
        bk = getBookByID(i.book)
        #bk.start = i.start
        #bk.end = i.end
        i.title=bk.title
        i.id=bk.id
        #print(bk.title, bk.start)
        r.append(i)
    return r

def getRequested(id):
    s = Request.query.filter_by(user=id).all()
    r = []
    for i in s:
        bk = getBookByID(i.book)
        i.title=bk.title
        r.append(i)
    return r

def getAllBooksFiltered(fbook, fauth, sort, section):
    des = False
    if sort == "rating" or sort == "reads":
        des = True
    try:
        sort = getattr(Book, sort)
    except:
        sort = Book.id
    
    
    if des:
        books = Book.query.filter(Book.title.like(fbook)).order_by(desc(sort)).all()
    else:
        books = Book.query.filter(Book.title.like(fbook)).order_by(asc(sort)).all()
    
    booksf=[]
    for i in books:
        bauth = Authorship.query.filter_by(book_id=i.id).all()
        bauthnames=[Author.query.filter_by(id=bl.author_id).first().name for bl in bauth]
        if len(bauthnames) == 0:
            i.authors = "N.A."
        else:
            i.authors = ",".join(bauthnames)
        if re.search(fauth, i.authors, re.IGNORECASE):
            if section != "":
                if Section_content.query.filter_by(book_id=i.id, section_id=section).first() != None:
                    booksf.append(i)    
            else:
                booksf.append(i)
    return booksf

##books functions
def getAllBooks():
    books = Book.query.all()
    for i in books:
        bauth = Authorship.query.filter_by(book_id=i.id).all()
        bauthnames=[Author.query.filter_by(id=bl.author_id).first().name for bl in bauth]
        if len(bauthnames) == 0:
            i.authors = "N.A."
        else:
            i.authors = ",".join(bauthnames)
    return books

def getBookByID(id):
    i = Book.query.filter_by(id=id).first()
    
    bauth = Authorship.query.filter_by(book_id=i.id).all()
    bauthnames=[Author.query.filter_by(id=bl.author_id).first().name for bl in bauth]
    i.bauth=[Author.query.filter_by(id=bl.author_id).first() for bl in bauth]
    if len(bauthnames) == 0:
        i.authors = "N.A."
    else:
        i.authors = ",".join(bauthnames)
    i.sections = []
    for sc in Section_content.query.filter_by(book_id=id).all():
        i.sections.append(Section.query.filter_by(id=sc.section_id).first())
    return i

def createAuthor(name):
    a = Author()
    a.name = name
    db.session.add(a)
    db.session.commit()
    return a

def addAuthorship(bid, aname):
    #print("=",author)
    a = Author.query.filter_by(name=aname).first()
    if a is None:
        a = createAuthor(aname)
    aship = Authorship()
    aship.book_id =bid
    aship.author_id = a.id
    try:
        db.session.add(aship)
        db.session.commit()
    except:
        pass

def createBook(name, desc, price):
    b = Book()
    b.title = name
    b.desc = desc
    b.price = price
    db.session.add(b)
    db.session.commit()
    return b

def updateBook(id,name, desc, price):
    b = getBookByID(id)
    b.title = name
    b.desc = desc
    b.price = price
    db.session.commit()
    return b


def deleteBook(id):
    b = Book.query.filter_by(id=id).first()

    #remove book from every section, issued, requests and history, and authorship, rating
    for sc in Section_content.query.filter_by(book_id=id).all():
        db.session.delete(sc)
    
    for i in Issued.query.filter_by(book=id).all():
        db.session.delete(i)
    
    for req in Request.query.filter_by(book=id).all():
        db.session.delete(req)
    
    for his in History.query.filter_by(book=id).all():
        db.session.delete(his)
    
    for auth in Authorship.query.filter_by(book_id=id).all():
        db.session.delete(auth)
    
    for r in Rating.query.filter_by(book=id).all():
        db.session.delete(r)

    for p in Purchase.query.filter_by(book_id=id).all():
        db.session.delete(p)
    for c in Comment.query.filter_by(book_id=id).all():
        db.session.delete(c)
    db.session.delete(b)
    db.session.commit()

##section functions
def getAllSections():
    return Section.query.all()

def createSection(name, description):
    s = Section()
    s.name = name
    s.description = description
    db.session.add(s)
    db.session.commit()
    return s

def updateSection(id,name, description):
    s = getSectionInfo(id)
    s.name = name
    s.description = description
    db.session.commit()
    return s

def modifySection(id, name, desc):
    s = Section.query.filter_by(id=id).first()
    s.name = name
    s.description = desc
    db.session.commit()

def deleteSection(id):
    s = Section.query.filter_by(id=id).first()
    for sc in Section_content.query.filter_by(section_id=id).all():
        db.session.delete(sc)
    db.session.delete(s)
    db.session.commit()

def getSectionInfo(sid):
    return Section.query.filter_by(id=sid).first()
def getSectionContent(sid):
    return Section_content.query.filter_by(section_id=sid).all()

def addSectionContent(bid, sid):
    try:
        sc = Section_content()
        sc.book_id = bid
        sc.section_id = sid
        db.session.add(sc)
        db.session.commit()
    except:
        pass

def delSectionContent(bid,sid):
    sc = Section_content.query.filter_by(book_id=bid, section_id=sid).first()
    db.session.delete(sc)
    db.session.commit()


def getPendingRequests():
    return Request.query.all()

def approveRequest(uid, bid):
    r = Request.query.filter_by(book=bid, user=uid).first()
    i = Issued()
    i.user = uid
    i.book = bid
    db.session.add(i)
    db.session.delete(r)
    db.session.commit()

def rejectRequest(uid, bid):
    r = Request.query.filter_by(book=bid, user=uid).first()
    db.session.delete(r)
    db.session.commit()


def getAllUsers():
    return User.query.filter_by(role="student").all()

def getAllAuthors():
    return Author.query.all()

def getPopularEbooks():
    return Book.query.order_by(desc(Book.reads)).limit(4).all()

def getLatestEbooks():
    return Book.query.order_by(desc(Book.id)).limit(4).all()

def getAllIssued():
    r = []
    maxBorrow = maxBorrowTime()
    for i in Issued.query.all():
        end = i.start + datetime.timedelta(days=maxBorrow)
        a = [i,getUserByID(i.user),getBookByID(i.book), end]
        r.append(a)
    return r

def flipTier(uid):
    u = getUserByID(uid)
    if u.tier == 1:
        u.tier = 0
    else:
        u.tier = 1
    db.session.commit()
    return u.tier

def getAllUsersFiltered(username, tier):
    
    users =[]
    if tier == -1:
        users = User.query.filter_by(role="student").filter(User.username.like(username)).all()
    else:
        users = User.query.filter_by(role="student").filter(User.username.like(username)).filter_by(tier=tier).all()
    return users

def getChartData_api():
    query = "select books.title, count(books.title) as num from issued,books where books.id = issued.book GROUP BY title order by num desc limit 5"
    r = db.session.execute(db.text(query))
    group = []
    data = []
    total = 0
    for i in r:
        group.append(i[0])
        data.append(i[1])
        total += i[1]
    group = [ '\n'.join(wrap(l, 20)) for l in group ]
    return {"group":group, "data":data}

def getChartData():
    query = "select books.title, count(books.title) as num from issued,books where books.id = issued.book GROUP BY title order by num desc limit 5"
    r = db.session.execute(db.text(query))
    group = []
    data = []
    total = 0
    for i in r:
        group.append(i[0])
        data.append(i[1])
        total += i[1]
    group = [ '\n'.join(wrap(l, 20)) for l in group ]
    plt.figure(figsize=(5, 3.5))
    plt.pie(data, labels=group, autopct=lambda x : int(x * total // 100))
    buff = io.BytesIO()
    plt.savefig(buff, format="png")
    buff.seek(0)
    return buff

def getAllHistory():
    r = []
    for i in History.query.all():
        a = [i,getUserByID(i.user),getBookByID(i.book)]
        r.append(a)
    return r

def getTimedHistory(f,l):
    r = []
    for i in History.query.filter(History.end >= f).filter(History.end <= l).all():
        a = [i,getUserByID(i.user),getBookByID(i.book)]
        r.append(a)
    return r

def getPreviousMonthRange():
    now = datetime.datetime.now()
    ft = datetime.datetime(now.year, now.month, 1)
    l = datetime.datetime(now.year, now.month, 1) - datetime.timedelta(days=1)
    l = l.replace(hour=23, minute=59, second=59)
    f = datetime.datetime(l.year, l.month, 1)
    return f, l


def getTimedReads(book_id, f, l):
    r = []
    ## get monthly reads for last month
    f,l = getPreviousMonthRange()
    his = History.query.filter(History.end >= f).filter(History.end <= l).filter_by(book=book_id).all()
    #for i in History.query.filter(History.end > datetime.datetime.now().replace(day=1, hour=0)).filter_by(book=book_id).all():
    for i in his:
        
        a = [i,getUserByID(i.user),getBookByID(i.book)]
        r.append(a)
    return len(r)

def mostReadBook(f,l):
    r = []
    
    for i in Book.query.all():
        a = [i, getTimedReads(i.id, f, l)]
        r.append(a)
    return max(r, key=lambda x: x[1])