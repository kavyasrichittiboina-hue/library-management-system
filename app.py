from flask import Flask,render_template,request,redirect,url_for,flash,session
import sqlite3
app=Flask(__name__)
app.secret_key = "library-secret-key"
def admin_required():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session["role"] != "Admin":
        return redirect(url_for("user_dashboard"))
    return None
@app.route("/login", methods=["GET", "POST"])
def login():
    connection = sqlite3.connect("library.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if request.method == "GET":
        connection.close()
        return render_template("login.html")
    login_id = request.form["login_id"]
    password = request.form["password"]
    cursor.execute("""SELECT UserId, LoginId, Password, Role FROM Users
        WHERE LoginId = ? AND Password = ?""", (login_id, password))
    user = cursor.fetchone()
    if user is None:
        connection.close()
        return render_template(
        "login.html",
        message="Invalid Login ID or Password")
    cursor.execute("""SELECT MemberId, MemberName, MemberType
    FROM Members WHERE LoginId = ?""", (login_id,))
    member = cursor.fetchone()
    connection.close()
    session["user_id"] = user["UserId"]
    session["login_id"] = user["LoginId"]
    session["role"] = user["Role"]
    if member:
        session["member_id"] = member["MemberId"]
        session["member_name"] = member["MemberName"]
        session["member_type"] = member["MemberType"]
    else:
        session["member_id"] = None
        session["member_name"] = None
        session["member_type"] = None
    if user["Role"] == "Admin":
        return redirect(url_for("admin_dashboard"))
    else:
        return redirect(url_for("user_dashboard"))
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
@app.route("/user_dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session["role"] == "Admin":
        return redirect(url_for("admin_dashboard"))
    return render_template("user_dashboard.html",login_id=session["login_id"],
        role=session["role"])
@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session["role"] != "Admin":
        return redirect(url_for("user_dashboard"))
    return render_template("admin_dashboard.html",
        login_id=session["login_id"])
#Home page

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session["role"] == "Admin":
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("user_dashboard"))
@app.route("/members")
def members():
    check = admin_required()
    if check:
        return check
    connection = sqlite3.connect("library.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""SELECT MemberId,MemberName,Email,
               Phone,MemberType,JoinDate,Status,LoginId
        FROM Members""")

    member = cursor.fetchall()
    connection.close()
    return render_template("members.html", member=member)

#Books page
@app.route("/books")
def books():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""select * from Books;""")
    book=cursor.fetchall()
    return render_template("books.html",book=book)

#Borrowing
@app.route("/borrowing")
def borrowing():
    if "user_id" not in session:
        return redirect(url_for("login"))
    connection = sqlite3.connect("library.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if session["role"] == "Admin":
        cursor.execute("""SELECT br.BorrowId,m.MemberName,m.MemberType,b.BookTitle,b.AccessLevel,
        br.BorrowDate,br.DueDate,br.ReturnDate,br.Status FROM Borrowing br
            JOIN Members m ON br.MemberId = m.MemberId
            JOIN Books b ON br.BookId = b.BookId""")
    else:
        cursor.execute(""" SELECT br.BorrowId,
                m.MemberName, m.MemberType, b.BookTitle, b.AccessLevel, br.BorrowDate,
                br.DueDate,br.ReturnDate,br.Status
            FROM Borrowing br JOIN Members m ON br.MemberId = m.MemberId JOIN Books b
              ON br.BookId = b.BookId WHERE br.MemberId = ?""", (session["member_id"],))
    borrow = cursor.fetchall()
    connection.close()
    return render_template("borrowing.html",borrow=borrow)

#Bookpricehistory
@app.route("/bookpricehistory")
def bookpricehistory():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""select * from Bookpricehistory;""")
    bookph=cursor.fetchall()
    return render_template("bookpricehistory.html",bookph=bookph)

#Fines
@app.route("/fines")
def fines():
    if "user_id" not in session:
        return redirect(url_for("login"))
    connection = sqlite3.connect("library.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if session["role"] == "Admin":
        cursor.execute("""SELECT *FROM Fines""")
    else:
        cursor.execute("""SELECT
                f.FineId,f.BorrowId,f.FineAmount,f.PaymentStatus FROM Fines f
            JOIN Borrowing br ON f.BorrowId = br.BorrowId WHERE br.MemberId = ?""", (session["member_id"],))
    fine = cursor.fetchall()
    connection.close()
    return render_template("fines.html",fine=fine)

#Acquistions
@app.route("/acquisitions")
def acquisitions():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""select * from Acquisitions;""")
    acqs=cursor.fetchall()
    return render_template("acquisition.html",acqs=acqs)

#AuditLog
@app.route("/auditlogs")
def auditlogs():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""select * from Auditlog;""")
    audits=cursor.fetchall()
    return render_template("auditlog.html",audits=audits)

@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    check = admin_required()
    if check:
        return check
    connection = sqlite3.connect("library.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if request.method == "GET":
        connection.close()
        return render_template("add_member.html")
    member_name = request.form["member_name"]
    email = request.form["email"]
    phone = request.form["phone"]
    member_type = request.form["member_type"]
    # Check whether email already exists
    cursor.execute("""SELECT MemberId FROM Members WHERE Email = ?""",(email,))
    existing_member = cursor.fetchone()
    if existing_member:
        connection.close()
        return render_template("add_member.html",message="Email already exists. Please use a different email.")
    cursor.execute("""INSERT INTO Members (MemberName, Email, Phone, MemberType) VALUES (?, ?, ?, ?)""", (member_name,email,phone,member_type))
    return redirect(url_for("members"))
#return books
@app.route("/returnbook",methods=["GET","POST"])
def return_book():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    if request.method=="GET":
        cursor.execute("""SELECT br.BorrowId, m.MemberName, b.BookTitle,
                br.BorrowDate,br.DueDate FROM Borrowing br JOIN Members m
                ON br.MemberId = m.MemberId JOIN Books b ON br.BookId = b.BookId
                WHERE br.Status = 'Borrowed'""")
        borrowings=cursor.fetchall()
        return render_template("returnbook.html",borrowings=borrowings)
    #selected borroiwng id
    borrow_id=request.form["borrow_id"]
    cursor.execute("""select * from Borrowing where BorrowId=? and Status='Borrowed'""",(borrow_id,))
    borrowing=cursor.fetchone()
    if borrowing is None:
        connection.close()
        return "Borrowing record not found"
    #Return Date
    from datetime import date
    return_date=date.today()
    #check late days
    due_date=date.fromisoformat(borrowing["DueDate"])
    late_days=(return_date-due_date).days
    #change borrowing status
    cursor.execute("""update Borrowing set ReturnDate=current_date,Status='Returned' where BorrowId=?""",(return_date.isoformat(),borrow_id))
    #increase available copies
    cursor.execute("""update Books set AvailableCopies=AvailableCopies+1 where BookId=?""",(borrowing["BookId"],))
    #create fine in late
    if late_days>0:
        fine_amount=late_days*10
        cursor.execute("""insert into Fines(BorrowId,Fineamount,Paymentstatus) values(?,?,'Due')""",
            borrow_id,fine_amount)

@app.route("/issuebook", methods=["GET", "POST"])
def issuebook():
    connection = sqlite3.connect("library.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    # GET → SHOW ISSUE BOOK FORM
    if request.method == "GET":
        cursor.execute("""SELECT * FROM Members WHERE Status = 'Active'""")
        members = cursor.fetchall()
        cursor.execute("""SELECT * FROM Books WHERE AvailableCopies > 0""")
        books = cursor.fetchall()
        connection.close()
        return render_template("issuebook.html",members=members,books=books)
    # POST → ISSUE BOOK
    member_id = request.form["member_id"]
    book_id = request.form["book_id"]
    due_date = request.form["due_date"]
    # 1. GET MEMBER
    cursor.execute("""SELECT * FROM Members WHERE MemberId = ?""", (member_id,))
    member = cursor.fetchone()
    if member is None:
        connection.close()
        return "Member not found."
    # 2. GET BOOK
    cursor.execute("""SELECT * FROM Books WHERE BookId = ?""", (book_id,))
    book = cursor.fetchone()
    if book is None:
        connection.close()
        return "Book not found."
    # 3. CHECK AVAILABLE COPIES
    if book["AvailableCopies"] <= 0:
        connection.close()
        return "Book is not available."
    # 4. CHECK UNPAID FINE
    cursor.execute("""SELECT COALESCE(SUM(f.FineAmount), 0) FROM Fines f JOIN Borrowing br ON f.BorrowId = br.BorrowId
    WHERE br.MemberId = ? AND f.PaymentStatus = 'Due' """, (member_id,))
    unpaid_amount = cursor.fetchone()[0]
    if unpaid_amount > 0:
        connection.close()
        return render_template("issuebook.html",members=[],books=[], error=f"Cannot issue book. Unpaid fine amount: ₹{unpaid_amount:.2f}")
    # 5. STUDENT MAXIMUM 3 BOOKS
    if member["MemberType"] == "Student":
        cursor.execute("""SELECT COUNT(*) FROM Borrowing WHERE MemberId = ?
            AND Status = 'Borrowed'""", (member_id,))
        active_books = cursor.fetchone()[0]
        if active_books >= 3:
            connection.close()
            return "Student cannot borrow more than 3 active books."
    # 6. CHECK BOOK ACCESS
    if(member["MemberType"] == "Student" and book["AccessLevel"] == "Teacher"):
        connection.close()
        return "Students cannot borrow teacher-only books."
    # 7. INSERT BORROWING
    cursor.execute("""INSERT INTO Borrowing(MemberId,BookId,DueDate,Status)VALUES (?, ?, ?, 'Borrowed')
    """,(member_id,book_id,due_date))
    # 8. DECREASE AVAILABLE COPIES
    cursor.execute("""UPDATE Books SET AvailableCopies = AvailableCopies - 1 WHERE BookId = ?""",(book_id,))
    # 9. SAVE
    connection.commit()
    connection.close()
    # 10. GO TO BORROWING PAGE
    return redirect(url_for("borrowing"))

@app.route("/pay_fine",methods=["GET","POST"])
def pay_fine():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    #Get -> Show unpaid fines
    if request.method=="GET":
        cursor.execute("""select f.FineID,f.FineAmount,f.PaymentStatus,m.MemberName,b.BookTitle from Fines f 
        join Borrowing br on f.BorrowId=br.BorrowId join Members m on br.MemberId=m.MemberId join Books b on 
        br.BookId=b.BookId where f.PaymentStatus='Due'""")
        fines=cursor.fetchall()
        connection.close()
        return render_template("pay_fine.html",fines=fines)
#post->pay selected fines
    fine_id=request.form["fine_id"]
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""update Fines set PaymentStatus='Paid' where FineID=? AND PaymentStatus='Due'""",(fine_id,))
    connection.commit()
    print("Fine updated:", cursor.rowcount)
    connection.close()
    return redirect(url_for("pay_fine"))
# add_book
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    connection = sqlite3.connect("library.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if request.method == "GET":
        connection.close()
        return render_template("add_book.html")
    book_title = request.form["book_title"]
    author = request.form["author"]
    category = request.form["category"]
    quantity = int(request.form["quantity"])
    access_level = request.form["access_level"]
    price = float(request.form["price"])
    cursor.execute("""INSERT INTO Books (BookTitle, Author, Category, Quantity,AccessLevel, AvailableCopies, Price)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",(book_title,author,category,quantity,access_level,quantity,price))
    return redirect(url_for("books", message="Book added successfully!"))
#add copies
@app.route("/add_copies",methods=["GET","POST"])
def add_copies():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    if request.method=="GET":
        cursor.execute("""select * from Books""")
        books=cursor.fetchall()
        connection.close()
        return render_template("add_copies.html",books=books)
    book_id=request.form["book_id"]
    quantity=request.form["quantity"]
    supplier=request.form["supplier"]
    purchase_price=request.form["purchase_price"]
    cursor.execute("""insert into Acquisitions(BookId,Quantity,Supplier,PurchasePrice) values(?,?,?,?)""",(book_id,quantity,supplier,purchase_price))
    connection.commit()
    connection.close()
    return redirect(url_for("books"))  

#update price
@app.route("/update_price",methods=["GET","POST"])
def update_price():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    if request.method=="GET":
        cursor.execute("""SELECT BookId,BookTitle,Price from Books order by BookTitle;""")
        books=cursor.fetchall()
        connection.close()
        return render_template("update_price.html",books=books)
    #post request
    book_id=request.form["book_id"]
    new_price=float(request.form["new_price"])
    #update price
    cursor.execute("""update Books set Price=? where BookId=?;""",(new_price,book_id))
    connection.commit()
    connection.close()
    return redirect(url_for("books"))
@app.route("/reports")
def reports():
    connection=sqlite3.connect("library.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""select count(*) as TotalBooks,sum(Quantity) as TotalCopies, sum(AvailableCopies) as AvailableCopies, sum(Quantity-AvailableCopies) as BorrowedCopies from Books;""")
    summary=cursor.fetchone() 
    cursor.execute("""select Borrowing.BorrowId,Members.MemberName,Books.BookTitle,Borrowing.BorrowDate,Borrowing.DueDate,Borrowing.Status from Borrowing 
    join Members on Borrowing.MemberId=Members.MemberId join Books on
    Borrowing.BookId=Books.BookId where Borrowing.Status='Borrowed' order by Borrowing.BorrowDate;""")
    borrowed_books=cursor.fetchall()
    #borrowed books
    cursor.execute("""select Borrowing.BorrowId,Members.MemberName,Books.BookTitle,Borrowing.BorrowDate,Borrowing.DueDate,Borrowing.Status from Borrowing join Members
    on Borrowing.MemberId=Members.MemberId join Books on Borrowing.BookId=Books.BookId where Borrowing.Status='Borrowed' and date(Borrowing.DueDate)<date('now')order by Borrowing.DueDate;""")
    overdue_books=cursor.fetchall()
    #Member Borrowing History
    cursor.execute("""select Members.MemberName,Books.BookTitle,Borrowing.BorrowDate,Borrowing.ReturnDate,Borrowing.Status from Borrowing join Members on 
    Borrowing.MemberId=Members.MemberId join Books on Borrowing.BookId=Books.BookId order by Members.MemberName,Borrowing.BorrowDate desc;""")
    member_history=cursor.fetchall()
    #Book Borrowing Report
    cursor.execute("""select Books.BookId,Books.BookTitle,Books.Author,Books.Category,count(Borrowing.BorrowId) as BorrowCount from Books left join Borrowing
    on Books.BookId=Borrowing.BookId group by Books.BookId,Books.BookTitle,Books.Author,Books.Category order by BorrowCount desc;""")
    book_borrowing=cursor.fetchall()
    #category-wise book report
    cursor.execute("""select Category,count(*) as BookCount,sum(Quantity) as TotalCopies,sum(AvailableCopies) as AvailableCopies from Books group by Category order by
    BookCount desc;""")
    category_report=cursor.fetchall()

    #Audit Log Report
    cursor.execute("""select LogId,Action,TableName,Record,Description,ActionDate from AuditLog order by ActionDate desc,LogId desc;""")
    audit_logs=cursor.fetchall()

    #Most Borrowed Books
    cursor.execute("""select Books.BookId,Books.BookTitle,Books.Author,count(Borrowing.BorrowId) as BorrowCount from Books left join
    Borrowing on Books.BookId=Borrowing.BookId group by Books.BookId,Books.BookTitle,Books.Author order by BorrowCount desc limit 5;""")
    top_books=cursor.fetchall()

    #most active members
    cursor.execute("""select Members.MemberId,Members.MemberName,Members.MemberType,count(Borrowing.BorrowId) as BorrowCount from Members left join
    Borrowing on Members.MemberId=Borrowing.MemberId group by Members.MemberId,Members.MemberName,Members.MemberType order by BorrowCount desc limit 5;""")
    active_members=cursor.fetchall()

    #fine collection report
    cursor.execute("""select count(*) as TotalFines,sum(FineAmount) as TotalFineAmount,sum(case when PaymentStatus='Paid' then FineAmount else 0 end) as PaidFineAmount,
    sum(case when PaymentStatus='Due' then FineAmount else 0 end) as DueFineAmount from Fines;""")
    fine_report = cursor.fetchone()

    #Available vs Borrowed copies
    cursor.execute("""select sum(Quantity) as TotalCopies,sum(AvailableCopies) as AvailableCopies,
    sum(Quantity - AvailableCopies) as BorrowedCopies from Books;""")
    copies_report=cursor.fetchone()

    #Acquisition Report
    cursor.execute("""select Acquisitions.AcquisitionId,Books.BookTitle,Acquisitions.Quantity,Acquisitions.Supplier,Acquisitions.PurchasePrice
    from Acquisitions join Books on Acquisitions.BookId=Books.BookId order by Acquisitions.PurchaseDate desc;""")
    acquisition_report=cursor.fetchall()

    #teacher vs student borrowing report
    cursor.execute("""select Members.MemberType,count(Borrowing.BorrowId) as BorrowCount from Members left join Borrowing on Members.MemberId=Borrowing.MemberId
    group by Members.MemberType order by BorrowCount desc;""")
    member_type_report=cursor.fetchall()
    connection.close()
    return render_template("reports.html",summary=summary,borrowed_books=borrowed_books,
        overdue_books=overdue_books,member_history=member_history,book_borrowing=book_borrowing,
        category_report=category_report,audit_logs=audit_logs,top_books=top_books,active_members=active_members,
        fine_report=fine_report,copies_report=copies_report,acquisition_report=acquisition_report,member_type_report=member_type_report)

if __name__=="__main__":
    app.run(debug=True)

