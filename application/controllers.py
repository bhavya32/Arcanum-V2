import calendar
import datetime
import os
import time
from flask import jsonify, request, send_file, send_from_directory
from flask import current_app as app
from werkzeug.utils import secure_filename

from flask_jwt_extended import create_access_token, jwt_required, JWTManager, current_user as curr_user

from .dbFunctions import AutoApprove, addAuthorship, addSectionContent, approveRequest, checkAA, checkIssued, checkPurchase, createBook, createComment, createRequest, createSection, delSectionContent, deleteAuthors, deleteBook, deleteComment, deleteSection, fetchAllRatings, fetchRating, flipTier, getAllBooks, getAllBooksFiltered, getAllIssued, getAllSections, getAllUsers, getAllUsersFiltered, getBookByID, getChartData_api, getComment, getComments, getIssued, getLatestEbooks, getPastIssued, getPendingRequests, getPopularEbooks, getPurchases, getRequestStatus, getRequested, getSectionContent, getSectionInfo, getUser, createUser, deleteUser, getUserByID, maxBorrowTime, maxIssueBooks, purchaseHistory, rejectRequest, returnBook, setRazID, updateBook, updateInfo, updatePolicy, updateRating, updateSection, createPurchase, completePurchase
from .models import Book
import hashlib
from .util import admin as adminFilter
from application import tasks
from .cache_setup import cache
from flask_cors import CORS
from .razor_config import client as razorpay_client
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = ".......4" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=15)
jwt = JWTManager(app)
recent_export_tasks=[]

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return getUser(identity)


##### razorpay

@app.route("/api/create_purchase_request", methods=["POST"])
@jwt_required()
def create_purchase_request():
    r = request.get_json()
    book_id = r["book_id"]
    user_id = curr_user.id
    amount = getBookByID(book_id).price
    purchase = createPurchase(user_id, book_id, amount)
    request_data = {
        "amount": amount * 100,
        "currency": "INR",
        "receipt": str(purchase),
    }
    payment = razorpay_client.order.create(data = request_data)
    setRazID(purchase, payment["id"])
    return jsonify(order_id=payment["id"])

@app.route("/api/verify_purchase", methods=["POST"])
@jwt_required()
def verify_purchase():
    r = request.get_json()
    result = razorpay_client.utility.verify_payment_signature(r)
    if result:
        completePurchase(r["razorpay_order_id"])
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})
#### razorpay end

@app.route("/api/sales_stats")
@jwt_required()
@adminFilter
def sales_stats():
    dt = datetime.datetime.now()
    last_date_num = calendar.monthrange(dt.year, dt.month)[1]
    last_date = f"{dt.year}-{dt.month:02d}-{dt.day:02d}"
    first_date = f"{dt.year}-{dt.month:02d}-01"
    data = purchaseHistory(first_date, last_date)
    return jsonify(data)

@app.route("/api/cache_test")
@cache.cached(timeout=20)
def cache_test():
    #wait for 10 seconds
    time.sleep(5)
    return jsonify({"status": "success"})


@app.route("/api/export")
@jwt_required()
@adminFilter
def export():
    #run after 15 seconds
    tsk = tasks.create_history_csv.apply_async(countdown=15)
    curr_time = datetime.datetime.now()
    recent_export_tasks.append({"task_id": tsk.id, "time": curr_time})
    return jsonify({"status": "success", "task_id": tsk.id})

@app.route("/api/export_status")
@jwt_required()
@adminFilter
def export_status():
    status = []
    for i in recent_export_tasks:
        task = tasks.create_history_csv.AsyncResult(i["task_id"])
        status.append({"task_id": i["task_id"], "status": task.status, "result": task.result, "time": i["time"]})
    return jsonify(status)

@app.route("/api/send_reminders")
@jwt_required()
@adminFilter
def send_reminders():
    tsk = tasks.return_reminder.apply_async()
    return jsonify({"status": "success", "task_id": tsk.id})

@app.route("/api/month_report")
@jwt_required()
@adminFilter
def month_report():
    tsk = tasks.monthly_activity.apply_async()
    return jsonify({"status": "success", "task_id": tsk.id})

@app.route("/api/sections")
def sections_api():
    sections = getAllSections()
    for i in sections:
        i.bc = len(getSectionContent(i.id))
    return jsonify([{"id": i.id, "name": i.name, "books_count": i.bc} for i in sections])

@app.route("/api/login", methods=["POST"])
def login_api():
    r = request.get_json()
    username = r["username"] 
    password = r["password"] 
    if not username or not password:
        return jsonify({"msg": "Bad username or password"}), 401
    # MD5 encrypt the password
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    userType = r["userType"] 
    user = getUser(username)
    if user != None and user.password == password and user.role == userType:
        access_token = create_access_token(identity=username, additional_claims={"role": user.role})
        return jsonify(access_token=access_token, username=user.username, role=user.role, name=user.fname + " " + user.lname, id=user.id), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401
 
@app.route("/api/usename_availability")
@cache.cached(timeout=60)
def username_availability():
    username = request.args["username"]
    user = getUser(username)
    available = True
    if user != None:
        available = False
    return jsonify({"available": available}), 200

@app.route("/api/change_info", methods=["POST"])
@jwt_required()
def change_info():
    r = request.get_json()
    fname = r["fname"]
    lname = r["lname"]
    email = r["email"]
    password = curr_user.password
    if r["password"] != "":
        password = hashlib.md5(r["password"].encode('utf-8')).hexdigest()
    updateInfo(curr_user.id, fname, lname, email, password)
    access_token = create_access_token(identity=curr_user.username, additional_claims={"role": curr_user.role})
    return jsonify(status="success",access_token=access_token, username=curr_user.username, role=curr_user.role, name=curr_user.fname + " " + curr_user.lname, id=curr_user.id)
    


@app.route("/api/register", methods=["POST"])
def register_api():
    r = request.get_json()
    fname = r["fname"]
    lname = r["lname"]
    username = r["username"]
    password = r["password"]
    email = r["email"]
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    user = getUser(username)
    if user != None:
        return jsonify({"msg": "Username already exists"}), 401
    user = createUser(fname, lname, username, password, email)
    access_token = create_access_token(identity=username, additional_claims={"role": user.role})
    return jsonify(status="success",access_token=access_token, username=user.username, role=user.role, name=user.fname + " " + user.lname, id=user.id)



@app.route("/api/home_books")
@cache.cached(timeout=300)
def home_books():
    #sections_c = getAllSections()
    sections= [{"id": i.id, "name": i.name} for i in getAllSections()]
    gs = [sections[i:i+4] for i in range(0, len(sections), 4)]
    popular = [{"id": i.id, "title": i.title} for i in getPopularEbooks()]
    latest = [{"id": i.id, "title": i.title} for i in getLatestEbooks()]
    return jsonify({"gs":gs, "popular":popular, "latest":latest})


@app.route("/api/admin/comments/<int:cid>/delete")
@jwt_required()
@adminFilter
def delete_comment_admin(cid):
    deleteComment(cid)
    return jsonify({"status": "success"})

@app.route("/api/comments/<int:bid>/delete")
@jwt_required()
def delete_comment_api(bid):
    c = getComment(curr_user.id, bid)
    if c == None:
        return jsonify({"status": "error", "msg": "Comment not found"})
    deleteComment(c.id)
    return jsonify({"status": "success"})

@app.route("/api/book/<int:bid>/comment", methods=["POST"])
@jwt_required()
def add_comment_api(bid):
    r = request.get_json()
    comment = r["comment"]
    #check if user has already commented
    c = getComment(curr_user.id, bid)
    if c != None:
        return jsonify({"status": "error", "msg": "You have already commented"})
    #check if user has rated
    r = fetchRating(curr_user.id, bid)
    if r == None:
        return jsonify({"status": "error", "msg": "You need to rate the book first"})
    # check if comment length is appropriate
    if len(comment)>500:
        return jsonify({"status": "error", "msg": "Comment too long"})
    createComment(curr_user.id, bid, comment)
    return jsonify({"status": "success"})

@app.route("/api/book/<int:bid>/comments")
@jwt_required()
def comments_api(bid):
    comments = getComments(bid)
    
    return jsonify(comments = comments)

@app.route("/api/rate/book/<int:bid>")
@jwt_required()
def rate_api(bid):
    uid = curr_user.id
    rating = request.args["rating"]
    updateRating(uid, bid, rating)
    return jsonify({"status": "success"})

@app.route("/api/book/<int:id>")
@jwt_required()
def book_api(id):
    book=getBookByID(id)
    issued = False
    score = 0
    rs = getRequestStatus(curr_user.id, book.id)
    requested =  rs.to_dict() if rs else False
    if curr_user.role=="student":
        issued = checkIssued(curr_user.id, book.id)
    curr = fetchRating(curr_user.id, id)
    if curr:
        score = curr.score
    owned = checkPurchase(curr_user.id, id)
    allratings = fetchAllRatings(id)
    allratings = [{"user": i.user, "score": i.score} for i in allratings]
    sections = [{"id": i.id, "name": i.name} for i in book.sections]
    tier = curr_user.tier
    bauth = [b.to_dict() for b in book.bauth]
    return jsonify({"book": {"id": book.id, "title": book.title, "desc": book.desc, "authors": bauth, "rating": book.rating, "reads": book.reads, "sections":sections,"price": book.price}, "issued": issued, "score": score, "allratings": allratings, "requested": requested, "tier": tier, "owned": owned})    


@app.route("/api/book/<int:id>/request")
@jwt_required()
def request_book_api(id):
    try:
        createRequest(curr_user.id, id)
    except:
        return jsonify({"status": "error", "msg": "You have reached the max borrowing cap. Please return a book and try again."})
    checkAA(curr_user.id, id)
    return jsonify({"status": "success"})


@app.route("/api/request/<int:bid>/cancel")
@jwt_required()
def request_cancel_api(bid):
    uid = curr_user.id
    rejectRequest(uid, bid)
    return jsonify({"status": "success"})


@app.route("/api/book/<int:bid>/section/<int:sid>/add")
@jwt_required()
@adminFilter
def section_book_add_api(bid, sid):
    addSectionContent(bid, sid)
    return jsonify({"status": "success"})


@app.route("/api/book/<int:bid>/section/<int:sid>/remove")
@jwt_required()
@adminFilter
def section_book_remove_api(bid, sid):
    delSectionContent(bid, sid)
    return jsonify({"status": "success"})


@app.route("/api/book/<int:id>/delete")
@jwt_required()
@adminFilter
def book_delete_api(id):
    deleteBook(id)
    return jsonify({"status": "success"})

@app.route("/api/books", methods=["POST"])
@jwt_required()
@adminFilter
def book_create_api():
    name=request.form["book_name"]
    desc=request.form["book_desc"]
    price=request.form["price"]
    #author=request.form["author_name"]
    authors = request.form.getlist("author_name")
    book = createBook(name,desc, price)
    try:
        pdf = request.files["book_pdf"]
        pdf.save(os.path.join("./static/pdfs", secure_filename(str(book.id) + ".pdf")))
    except:
        pass
    try:
        img=request.files["book_img"]
        if img.filename != "":
            img.save(os.path.join("./static/books", secure_filename(str(book.id))))
    except:
        pass
    for i in authors:
        addAuthorship(book.id, i)
    return jsonify({"status": "success", "id": book.id})


@app.route("/api/section/<int:id>")
def section_api(id):
    s = getSectionInfo(id)
    books = getSectionContent(id)
    books_r = []
    for i in books:
        books_r += [Book.query.filter_by(id=i.book_id).first().to_dict()]
    return jsonify({"section": s.to_dict(), "books": books_r})



@app.route("/api/section/<int:id>/delete")
@jwt_required()
@adminFilter
def section_delete_api(id):
    deleteSection(id)
    return jsonify({"status": "success"})


@app.route("/api/sections", methods=["POST"])
@jwt_required()
@adminFilter
def section_create_api():
    name=request.form["section_name"]
    desc=request.form["section_desc"]
    s = createSection(name,desc)
    try:
        file=request.files["section_img"]
        if file.filename != "":
            file.save(os.path.join("./static/sections", secure_filename(str(s.id))))
    except:
        pass
    return jsonify({"status": "success", "id": s.id})


@app.route("/api/adminDashboard")
@jwt_required()
@adminFilter
def admin_dashboard_api():
    requests = getPendingRequests()
    users = getAllUsers()
    sections = getAllSections()
    books= getAllBooks()
    issued = getAllIssued()
    return jsonify({"req": len(requests), "users": len(users), "sections": len(sections), "books": len(books), "issued": len(issued), "mxd": maxBorrowTime(), "mxc": maxIssueBooks(), "auto": AutoApprove()})



uniq_ids = {}
@app.route("/api/download")
def download():
    uid = request.args["id"]
    if uid not in uniq_ids:
        return jsonify({"status": "error", "msg": "Invalid id"})
    bid = uniq_ids[uid]
    return send_file(f"./static/pdfs/{bid}.pdf", as_attachment=False, download_name="book.pdf")

@app.route("/api/book/<int:bid>/download", methods=["GET"])
@jwt_required()
def download_req(bid):
    book = getBookByID(bid)
    if book == None:
        return jsonify({"status": "error", "msg": "User or book not found"})
    ## check if user has purchased
    if not checkPurchase(curr_user.id, bid):
        # check if user has issued
        if not checkIssued(curr_user.id, bid):
            return jsonify({"status": "error", "msg": "User has not issued this book"})
        if curr_user.tier == 0:
            return jsonify({"status": "error", "msg": "User is not allowed to download this book"})

    ##create  a unique id for the download
    uid = hashlib.md5(str(curr_user.id).encode('utf-8')).hexdigest()
    uniq_ids[uid] = bid
    return jsonify({"status": "success", "id": uid})

@app.route("/api/admin/chart")
@jwt_required()
@adminFilter
def admin_chart():
    data = getChartData_api()
    return jsonify(data)

@app.route("/api/admin/policy")
@jwt_required()
@adminFilter
def admin_policy():
    #get params from query
    t = ["MaxBorrowDays", "MaxBorrowBooks", "AutoApprove"]
    for i in t:
        x = request.args.get(i)
        updatePolicy(i, request.args.get(i))
    return jsonify({"status": "success"})


@app.route("/api/search")
def search_books():
    fbook = "%%"
    fauth = ""
    section= ""
    sort = "id"
    if "sort" in request.args:
        sort = request.args["sort"]
    if "book" in request.args:
        fbook = "%" + request.args["book"] + "%"
    if "author" in request.args:
        fauth = request.args["author"]
    if "section" in request.args:
        section = request.args["section"]
    
    books = getAllBooksFiltered(fbook, fauth,sort, section)
    return jsonify([{"id": i.id, "title": i.title, "authors": i.authors, "rating": i.rating, "reads": i.reads} for i in books])


@app.route("/api/request/<int:uid>/<int:bid>/approve")
@jwt_required()
@adminFilter
def request_approve_api(uid, bid):
    approveRequest(uid, bid)
    return jsonify({"status": "success"})


@app.route("/api/request/<int:uid>/<int:bid>/reject")
@jwt_required()
@adminFilter
def request_reject_api(uid, bid):
    rejectRequest(uid, bid)
    return jsonify({"status": "success"})


@app.route("/api/requests")
@jwt_required()
@adminFilter
def pending_requests_api():
    req = getPendingRequests()
    l = []
    for i in req:
        x = {}
        x["created_at"] = i.created_at
        book = getBookByID(i.book)
        x["book_name"] = book.title
        x["book_id"] = book.id
        user = getUserByID(i.user)
        x["username"] = user.username
        x["user_id"] = user.id
        l.append(x)
    
    return jsonify(l)

@app.route("/api/issued")
@jwt_required()
@adminFilter
def issued_books_api():
    return jsonify([{"username":i[1].username, "user_id":i[1].id, "book_name": i[2].title, "book_id":i[2].id, "start":i[0].start, "end":i[3]} for i in getAllIssued()])

@app.route("/api/book/<int:bid>/return")
@jwt_required()
def return_book_api(bid):
    returnBook(curr_user.id, bid)
    return jsonify({"status": "success"})

@app.route("/api/revoke/<int:uid>/<int:bid>")
@jwt_required()
@adminFilter
def revoke_book_api(uid, bid):
    returnBook(uid, bid)
    return jsonify({"status": "success"})

@app.route("/api/users")
@jwt_required()
@adminFilter
def users_api():
    fusername = "%%"
    tier = -1
    if "username" in request.args:
        fusername = "%" + request.args["username"] + "%"
    if "tier" in request.args and request.args["tier"].isdigit():
        tier = int(request.args["tier"])
    
    users = getAllUsersFiltered(fusername, tier)
    return jsonify([i.to_dict() for i in users])


@app.route("/api/user_info/<int:uid>")
@jwt_required()
@adminFilter
def my_details(uid):
    user = getUserByID(uid)
    books = getIssued(uid)
    past = getPastIssued(uid)
    req = getRequested(uid)
    pur = getPurchases(uid)
    for i in range(len(books)):
        issued = books[i].start
        books[i] = getBookByID(books[i].book).to_dict()
        books[i]["start"] = issued
        books[i]["end"] = issued + datetime.timedelta(days=maxBorrowTime())
    return jsonify({"user": user.to_dict(), "books": books, "past": [i.to_dict() for i in past], "req": [i.to_dict() for i in req], "pur": [i.to_dict() for i in pur]})


@app.route("/api/user_info")
@jwt_required()
def user_info_api():
    uid = curr_user.id
    user = curr_user
    books = getIssued(uid)
    past = getPastIssued(uid)
    req = getRequested(uid)
    pur = getPurchases(uid)
    for i in range(len(books)):
        issued = books[i].start
        books[i] = getBookByID(books[i].book).to_dict()
        books[i]["start"] = issued
        books[i]["end"] = issued + datetime.timedelta(days=maxBorrowTime())
    return jsonify({"user": user.to_dict(), "books": books, "past": [i.to_dict() for i in past], "req": [i.to_dict() for i in req],"pur": [i.to_dict() for i in pur]})


@app.route("/api/user/<int:uid>/delete")
@jwt_required()
@adminFilter
def delete_user_api(uid):
    deleteUser(uid)
    return jsonify({"status": "success"})

@app.route("/api/user/<int:uid>/flipTier")
@jwt_required()
@adminFilter
def tier_user_api(uid):
    tier = flipTier(uid)
    return jsonify({"status": "success", "tier": tier})

@app.route("/api/book/<int:id>/edit", methods=["POST"])
@jwt_required()
@adminFilter
def book_edit_api(id):
    name=request.form["book_name"]
    desc=request.form["book_desc"]
    price=request.form["price"]
    #author=request.form["author_name"]
    authors = request.form.getlist("author_name")
    book = updateBook(id, name,desc, price)
    try:
        pdf = request.files["book_pdf"]
        if pdf.filename != "":
            pdf.save(os.path.join("./static/pdfs", secure_filename(str(book.id) + ".pdf")))
    except:
        pass
    try:
        img=request.files["book_img"]
        if img.filename != "":
            img.save(os.path.join("./static/books", secure_filename(str(book.id))))
    except:
        pass
    deleteAuthors(id)
    for i in authors:
        addAuthorship(id, i)
    return jsonify({"status": "success"})



@app.route("/api/section/<int:id>/edit", methods=["POST"])
@jwt_required()
@adminFilter
def section_edit_api(id):
    name=request.form["section_name"]
    desc=request.form["section_desc"]
    s = updateSection(id, name,desc)
    try:
        file=request.files["section_img"]
        if file.filename != "":
            file.save(os.path.join("./static/sections", secure_filename(str(s.id))))
    except:
        pass
    return jsonify({"status": "success"})


@app.route('/<path:filename>')
def custom_static(filename):
    return send_from_directory('static/test', filename)
