import datetime
import os
from flask import jsonify, request, redirect, send_file, url_for
from flask import render_template
from flask import current_app as app
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required, login_user, logout_user
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, current_user as curr_user
from .database import login_manager
from .dbFunctions import AutoApprove, addAuthorship, addSectionContent, approveRequest, checkAA, checkIssued, createBook, createRequest, createSection, delSectionContent, deleteAuthors, deleteBook, deleteSection, fetchAllRatings, fetchRating, flipTier, getAllAuthors, getAllBooks, getAllBooksFiltered, getAllIssued, getAllSections, getAllUsers, getAllUsersFiltered, getBookByID, getChartData, getChartData_api, getIssued, getLatestEbooks, getPastIssued, getPendingRequests, getPopularEbooks, getRequestStatus, getRequested, getSectionContent, getSectionInfo, getUser, createUser, deleteUser, getUserByID, maxBorrowTime, maxIssueBooks, rejectRequest, returnBook, updateBook, updateInfo, updatePolicy, updateRating, updateSection
from .models import Book
import hashlib
from .util import librarian, admin as adminFilter
from application import tasks

from flask_cors import CORS
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["JWT_SECRET_KEY"] = ".......4" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=15)
jwt = JWTManager(app)
recent_export_tasks=[]

@app.route("/api/just_simple_task")
def just_simple_task():
    tsk = tasks.create_history_csv.delay()
    return jsonify({"status": "success", "task_id": tsk.id})

@app.route("/api/just_simple_task_status")
def just_simple_task_status():
    task_id = request.args["task_id"]
    task = tasks.create_history_csv.AsyncResult(task_id)
    return jsonify({"status": task.status, "result": task.result})

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return getUser(identity)
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    #current_user = get_jwt_identity()
    return jsonify(logged_in_as=curr_user.id), 200

@app.route("/protected2", methods=["GET"])
@jwt_required()
@adminFilter
def protected2():
    #current_user = get_jwt_identity()
    return jsonify(logged_in_as=curr_user.fname), 200



@login_manager.user_loader
def load_user(user_id):
    return getUser(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

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
    
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return jsonify({"msg": "Bad username or password"}), 401
        # MD5 encrypt the password
        password = hashlib.md5(password.encode('utf-8')).hexdigest()
        userType = request.form.get("userType")
        user = getUser(username)
        
        if user != None and user.password == password and user.role == userType:
            login_user(user, remember=True)
            if user.role == "librarian":
                return redirect(url_for("admin"))
            return redirect(url_for('profile'))
        else:
            msg = "Incorrect Credentials/Role"
            #return jsonify({"msg": "Bad username or password"}), 401
            return redirect(url_for('login'))
    return render_template("login.html", msg=msg)


@app.route("/api/usename_availability")
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        username = request.form.get("username")
        password = request.form.get("password")

        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        user = getUser(username)
        if user != None:
            #return redirect(url_for("register"))
            return render_template("register.html", msg = "Username already exists")
        user = createUser(fname, lname, username, password)
        login_user(user, remember=True)
        return redirect(url_for('profile'))
    else:
        return render_template("register.html")




@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/error")
def error():
    ed = "Error Details Unknown"
    if "err" in request.args:
        ed = request.args['err']
    return render_template("error.html", ed=ed)


@app.route("/api/home_books")
def home_books():
    #sections_c = getAllSections()
    sections= [{"id": i.id, "name": i.name} for i in getAllSections()]
    gs = [sections[i:i+4] for i in range(0, len(sections), 4)]
    popular = [{"id": i.id, "title": i.title} for i in getPopularEbooks()]
    latest = [{"id": i.id, "title": i.title} for i in getLatestEbooks()]
    return jsonify({"gs":gs, "popular":popular, "latest":latest})

@app.route("/")
def index():
    loggedin = current_user.is_authenticated
    sections = getAllSections()
    gs = [sections[i:i+4] for i in range(0, len(sections), 4)]
    popular = getPopularEbooks()
    latest = getLatestEbooks()
    return render_template("index.html", loggedin=loggedin, gs = gs, popular = popular, latest=latest)

@app.route("/return/<int:bid>")
@login_required
def return_book(bid):
    returnBook(current_user.id, bid)
    return redirect(url_for("profile"))

@app.route("/profile")
@login_required
def profile():
    user = getUserByID(current_user.id)
    books = getIssued(current_user.id)
    past = getPastIssued(current_user.id)
    req = getRequested(current_user.id)
    for i in range(len(books)):
        issued = books[i].start
        books[i] = getBookByID(books[i].book)
        books[i].start = issued
        books[i].end = issued + datetime.timedelta(days=maxBorrowTime())
    return render_template("profile.html", books=books, past=past, req=req,user=user)

@app.route("/api/rate/book/<int:bid>")
@jwt_required()
def rate_api(bid):
    uid = curr_user.id
    rating = request.args["rating"]
    updateRating(uid, bid, rating)
    return jsonify({"status": "success"})

@app.route("/rate/book/<int:bid>", methods=["GET"])
@login_required
def rate(bid):
    uid = current_user.id
    rating = request.args["rating"]
    updateRating(uid, bid, rating)
    return redirect(url_for("book", id=bid))

# Crud API for books
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
    allratings = fetchAllRatings(id)
    allratings = [{"user": i.user, "score": i.score} for i in allratings]
    sections = [{"id": i.id, "name": i.name} for i in book.sections]
    tier = curr_user.tier
    bauth = [b.to_dict() for b in book.bauth]
    return jsonify({"book": {"id": book.id, "title": book.title, "desc": book.desc, "authors": bauth, "rating": book.rating, "reads": book.reads, "sections":sections}, "issued": issued, "score": score, "allratings": allratings, "requested": requested, "tier": tier})    

@app.route("/book/<int:id>", methods=["GET"])
@login_required
def book(id):
    book=getBookByID(id)
    issued = False
    score = 0
    requested = getRequestStatus(current_user.id, book.id) or False
    if current_user.role=="student":
        issued = checkIssued(current_user.id, book.id)
        curr = fetchRating(current_user.id, id)
        if curr:
            score = curr.score
    allratings = fetchAllRatings(id)
    return render_template("book.html", book=book, user=current_user, sections=getAllSections(), issued=issued, score = score, allratings= allratings, requested= requested)


@app.route("/api/book/<int:id>/request")
@jwt_required()
def request_book_api(id):
    try:
        createRequest(curr_user.id, id)
    except:
        return jsonify({"status": "error", "msg": "You have reached the max borrowing cap. Please return a book and try again."})
    checkAA(curr_user.id, id)
    return jsonify({"status": "success"})

@app.route("/book/<int:id>/request", methods=["GET"])
@login_required
def request_book(id):
    try:
        createRequest(current_user.id, id)
    except:
        return redirect(url_for("error", err="You have reached the max borrowing cap. Please return a book and try again."))
    checkAA(current_user.id, id)
    return redirect(url_for("book", id=id))

@app.route("/api/request/<int:bid>/cancel")
@jwt_required()
def request_cancel_api(bid):
    uid = curr_user.id
    rejectRequest(uid, bid)
    return jsonify({"status": "success"})

@app.route("/requests/<int:bid>/cancel")
@login_required
def request_cancel(bid):
    uid = current_user.id
    rejectRequest(uid, bid)
    return redirect(url_for("profile"))

@app.route("/api/book/<int:bid>/section/<int:sid>/add")
@jwt_required()
@adminFilter
def section_book_add_api(bid, sid):
    addSectionContent(bid, sid)
    return jsonify({"status": "success"})

@app.route("/book/<int:bid>/sections/add")
@login_required
@librarian
def section_book_add(bid):
    sid=request.args["sid"]
    addSectionContent(bid, sid)
    return redirect(url_for("book", id=bid))


@app.route("/api/book/<int:bid>/section/<int:sid>/remove")
@jwt_required()
@adminFilter
def section_book_remove_api(bid, sid):
    delSectionContent(bid, sid)
    return jsonify({"status": "success"})

@app.route("/book/<int:bid>/sections/remove")
@login_required
@librarian
def section_book_remove(bid):
    sid = request.args["sid"]
    delSectionContent(bid, sid)
    return redirect(url_for("book", id=bid))

@app.route("/book/<int:bid>/sections/remove2")
@login_required
@librarian
def section_book_remove2(bid):
    sid = request.args["sid"]
    delSectionContent(bid, sid)
    return redirect(url_for("section", id=sid))

@app.route("/book/<int:id>/read", methods=["GET"])
@login_required
def book_read(id):
    return render_template("book_read.html", id=id)


@app.route("/api/book/<int:id>/delete")
@jwt_required()
@adminFilter
def book_delete_api(id):
    deleteBook(id)
    return jsonify({"status": "success"})

@app.route("/book/<int:id>/delete", methods=["GET"])
@login_required
@librarian
def book_delete(id):
    deleteBook(id)
    return redirect(url_for("books_list"))


@app.route("/api/books", methods=["POST"])
@jwt_required()
@adminFilter
def book_create_api():
    name=request.form["book_name"]
    desc=request.form["book_desc"]
    #author=request.form["author_name"]
    authors = request.form.getlist("author_name")
    book = createBook(name,desc)
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

@app.route("/books", methods=["POST"])
@login_required
@librarian
def book_create():
    name=request.form["book_name"]
    desc=request.form["book_desc"]
    #author=request.form["author_name"]
    authors = request.form.getlist("author_name")
    book = createBook(name,desc)
    
    img=request.files["book_img"]
    pdf = request.files["book_pdf"]
    pdf.save(os.path.join("./static/pdfs", secure_filename(str(book.id) + ".pdf")))
    
    if img.filename != "":
        img.save(os.path.join("./static/books", secure_filename(str(book.id))))
    for i in authors:
        addAuthorship(book.id, i)
    return redirect(url_for("book", id=book.id))

@app.route("/api/section/<int:id>")
def section_api(id):
    s = getSectionInfo(id)
    books = getSectionContent(id)
    books_r = []
    for i in books:
        books_r += [Book.query.filter_by(id=i.book_id).first().to_dict()]
    return jsonify({"section": s.to_dict(), "books": books_r})


@app.route("/section/<int:id>", methods=["GET"])
@login_required
def section(id):
    s = getSectionInfo(id)
    
    books = getSectionContent(id)
    books_r = []
    for i in books:
        books_r += [Book.query.filter_by(id=i.book_id).first()]
    return render_template("section.html", books=books_r, s=s, count=len(books_r))

@app.route("/api/section/<int:id>/delete")
@jwt_required()
@adminFilter
def section_delete_api(id):
    deleteSection(id)
    return jsonify({"status": "success"})

@app.route("/section/<int:id>/delete", methods=["GET"])
@login_required
@librarian
def section_delete(id):
    deleteSection(id)
    return redirect(url_for("sections_list"))

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

@app.route("/sections", methods=["POST"])
@login_required
@librarian
def section_create():
    #print(request.form)
    name=request.form["section_name"]
    desc=request.form["section_desc"]
    #print(name,desc)
    #print(request.files)
    s = createSection(name,desc)
    file=request.files["section_img"]
    if file.filename != "":
        file.save(os.path.join("./static/sections", secure_filename(str(s.id))))
    return redirect(url_for("section", id=s.id))

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

##librarian section
@app.route("/admin")
@login_required
@librarian
def admin():
    requests = getPendingRequests()
    users = getAllUsers()
    sections = getAllSections()
    books= getAllBooks()
    issued = getAllIssued()
    return render_template("admin.html", req=len(requests), users=len(users), sections=len(sections), books=len(books), issued = len(issued), mxd=maxBorrowTime(), mxc = maxIssueBooks(), auto=AutoApprove())

@app.route("/adminchart")
@login_required
@librarian
def adminchart():
    buff = getChartData()
    return send_file(buff, mimetype='image/jpg')

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


@app.route("/admin", methods=["POST"])
@login_required
@librarian
def admin_u():
    t = ["MaxBorrowDays", "MaxBorrowBooks", "AutoApprove"]
    for i in t:
        x = request.form.get(i)
        updatePolicy(i, request.form.get(i))

    return redirect(url_for("admin"))

@app.route("/sections")
@login_required
def sections_list():
    sections = getAllSections()
    for i in sections:
        i.bc = len(getSectionContent(i.id))
    return render_template("sections.html", sc = sections)

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

@app.route("/books")
@login_required
def books_list():
    
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
    filters = [fbook[1:-1], fauth, section, sort]
    return render_template("books.html", books=books, sections=getAllSections(), filters =filters)

@app.route("/admin/sections/create")
@login_required
@librarian
def section_add():
    return render_template("admin/section_add.html")

@app.route("/admin/books/create")
@login_required
@librarian
def book_add():
    authors = [a.name for a in getAllAuthors()]

    return render_template("admin/book_add.html", authors = authors)

@app.route("/api/request/<int:uid>/<int:bid>/approve")
@jwt_required()
@adminFilter
def request_approve_api(uid, bid):
    approveRequest(uid, bid)
    return jsonify({"status": "success"})

@app.route("/admin/requests/approve/<int:uid>/<int:bid>")
@login_required
@librarian
def request_approve(uid, bid):
    approveRequest(uid, bid)
    if "return" in request.args:
        return redirect(url_for("user_details",uid=uid))
    return redirect(url_for("pending_requests"))

@app.route("/api/request/<int:uid>/<int:bid>/reject")
@jwt_required()
@adminFilter
def request_reject_api(uid, bid):
    rejectRequest(uid, bid)
    return jsonify({"status": "success"})

@app.route("/admin/requests/reject/<int:uid>/<int:bid>")
@login_required
@librarian
def request_reject(uid, bid):
    rejectRequest(uid, bid)
    if "return" in request.args:
        return redirect(url_for("user_details",uid=uid))
    return redirect(url_for("pending_requests"))


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

@app.route("/admin/requests")
@login_required
@librarian
def pending_requests():
    req = getPendingRequests()
    l = []
    for i in req:
        l.append([i, getBookByID(i.book), getUserByID(i.user)])
    
    return render_template("admin/requests.html", req=l)

@app.route("/api/issued")
@jwt_required()
@adminFilter
def issued_books_api():
    return jsonify([{"username":i[1].username, "user_id":i[1].id, "book_name": i[2].title, "book_id":i[2].id, "start":i[0].start, "end":i[3]} for i in getAllIssued()])

@app.route("/admin/issued")
@login_required
@librarian
def issued_books():
    return render_template("admin/issued.html", issued = getAllIssued())

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

@app.route("/admin/issued/revoke/<int:uid>/<int:bid>")
@login_required
@librarian
def revoke_book(uid, bid):
    returnBook(uid, bid)
    if "return" in request.args:
        return redirect(url_for("user_details",uid=uid))
    else:
        return redirect(url_for("issued_books"))

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

@app.route("/admin/users")
@login_required
@librarian
def active_users():
    fusername = "%%"
    tier = -1
    if "username" in request.args:
        fusername = "%" + request.args["username"] + "%"
    if "tier" in request.args and request.args["tier"].isdigit():
        tier = int(request.args["tier"])
    
    users = getAllUsersFiltered(fusername, tier)
    return render_template("admin/users.html", users = users)


@app.route("/api/user_info/<int:uid>")
@jwt_required()
@adminFilter
def my_details(uid):
    user = getUserByID(uid)
    books = getIssued(uid)
    past = getPastIssued(uid)
    req = getRequested(uid)
    for i in range(len(books)):
        issued = books[i].start
        books[i] = getBookByID(books[i].book).to_dict()
        books[i]["start"] = issued
        books[i]["end"] = issued + datetime.timedelta(days=maxBorrowTime())
    return jsonify({"user": user.to_dict(), "books": books, "past": [i.to_dict() for i in past], "req": [i.to_dict() for i in req]})


@app.route("/api/user_info")
@jwt_required()
def user_info_api():
    uid = curr_user.id
    user = curr_user
    books = getIssued(uid)
    past = getPastIssued(uid)
    req = getRequested(uid)
    for i in range(len(books)):
        issued = books[i].start
        books[i] = getBookByID(books[i].book).to_dict()
        books[i]["start"] = issued
        books[i]["end"] = issued + datetime.timedelta(days=maxBorrowTime())
    return jsonify({"user": user.to_dict(), "books": books, "past": [i.to_dict() for i in past], "req": [i.to_dict() for i in req]})

@app.route("/admin/user/<int:uid>")
@login_required
@librarian
def user_details(uid):
    user = getUserByID(uid)
    books = getIssued(uid)
    past = getPastIssued(uid)
    req = getRequested(uid)
    for i in range(len(books)):
        issued = books[i].start
        books[i] = getBookByID(books[i].book)
        books[i].start = issued
        books[i].end = issued + datetime.timedelta(days=maxBorrowTime())
    return render_template("admin/user.html", books=books, past=past, req=req, user = user)

@app.route("/api/user/<int:uid>/delete")
@jwt_required()
@adminFilter
def delete_user_api(uid):
    deleteUser(uid)
    return jsonify({"status": "success"})

@app.route("/admin/user/<int:uid>/delete")
@login_required
@librarian
def delete_user(uid):
    deleteUser(uid)
    return redirect(url_for("active_users"))

@app.route("/api/user/<int:uid>/flipTier")
@jwt_required()
@adminFilter
def tier_user_api(uid):
    tier = flipTier(uid)
    return jsonify({"status": "success", "tier": tier})

@app.route("/admin/user/<int:uid>/flipTier")
@login_required
@librarian
def tier_user(uid):
    flipTier(uid)
    return redirect(url_for("active_users"))

@app.route("/book/<int:id>/edit", methods=["GET"])
@login_required
@librarian
def book_edit_view(id):
    book=getBookByID(id)
    return render_template("admin/book_edit.html", book=book)

@app.route("/api/book/<int:id>/edit", methods=["POST"])
@jwt_required()
@adminFilter
def book_edit_api(id):
    name=request.form["book_name"]
    desc=request.form["book_desc"]
    #author=request.form["author_name"]
    authors = request.form.getlist("author_name")
    book = updateBook(id, name,desc)
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

@app.route("/book/<int:id>/edit", methods=["POST"])
@login_required
@librarian
def book_edit(id):
    name=request.form["book_name"]
    desc=request.form["book_desc"]
    #author=request.form["author_name"]
    authors = request.form.getlist("author_name")
    book = updateBook(id, name,desc)
    
    img=request.files["book_img"]
    pdf = request.files["book_pdf"]
    if pdf.filename != "":
        pdf.save(os.path.join("./static/pdfs", secure_filename(str(book.id) + ".pdf")))
    if img.filename != "":
        img.save(os.path.join("./static/books", secure_filename(str(book.id))))
    deleteAuthors(id)
    for i in authors:
        addAuthorship(id, i)
    return redirect(url_for("book", id=id))

@app.route("/section/<int:id>/edit", methods=["GET"])
@login_required
@librarian
def section_edit_view(id):
    section=getSectionInfo(id)
    return render_template("admin/section_edit.html", s=section)


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

@app.route("/section/<int:id>/edit", methods=["POST"])
@login_required
@librarian
def section_edit(id):
    name=request.form["section_name"]
    desc=request.form["section_desc"]
    s = updateSection(id, name,desc)
    file=request.files["section_img"]
    if file.filename != "":
        file.save(os.path.join("./static/sections", secure_filename(str(s.id))))
    return redirect(url_for("section", id=id))


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "student":
        return redirect(url_for("profile"))
    else:
        return redirect(url_for("admin"))