import sqlite3

# ==========================================
# CONNECT TO DATABASE
# ==========================================

connection = sqlite3.connect("library.db")
cursor = connection.cursor()

cursor.execute("PRAGMA foreign_keys = ON")


# ==========================================
# MEMBERS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Members(
    MemberId INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberName TEXT NOT NULL,
    Email TEXT UNIQUE,
    Phone TEXT,
    MemberType TEXT NOT NULL
        CHECK(MemberType IN ('Teacher', 'Student')),
    JoinDate DATE DEFAULT CURRENT_DATE,
    Status TEXT DEFAULT 'Active',
    LoginId TEXT UNIQUE
)
""")


# ==========================================
# BOOKS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Books(
    BookId INTEGER PRIMARY KEY AUTOINCREMENT,
    BookTitle TEXT NOT NULL,
    Author TEXT NOT NULL,
    Category TEXT,
    Quantity INTEGER NOT NULL DEFAULT 0,
    AccessLevel TEXT NOT NULL
        CHECK(AccessLevel IN ('Teacher', 'Student')),
    AvailableCopies INTEGER NOT NULL DEFAULT 0,
    Price REAL
)
""")


# ==========================================
# USERS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users(
    UserId INTEGER PRIMARY KEY AUTOINCREMENT,
    LoginId TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    Role TEXT NOT NULL
)
""")


# ==========================================
# BORROWING TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Borrowing(
    BorrowId INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberId INTEGER NOT NULL,
    BookId INTEGER NOT NULL,
    BorrowDate DATE DEFAULT CURRENT_DATE,
    DueDate DATE NOT NULL,
    ReturnDate DATE,
    Status TEXT DEFAULT 'Borrowed'
        CHECK(Status IN ('Borrowed', 'Returned')),
    FOREIGN KEY(MemberId) REFERENCES Members(MemberId),
    FOREIGN KEY(BookId) REFERENCES Books(BookId)
)
""")


# ==========================================
# FINES TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Fines(
    FineID INTEGER PRIMARY KEY AUTOINCREMENT,
    BorrowId INTEGER,
    Fineamount REAL,
    Paymentstatus TEXT NOT NULL
        CHECK(Paymentstatus IN ('Paid', 'Due')),
    FOREIGN KEY(BorrowId) REFERENCES Borrowing(BorrowId)
)
""")


# ==========================================
# ACQUISITIONS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Acquisitions(
    AcquisitionId INTEGER PRIMARY KEY AUTOINCREMENT,
    BookId INTEGER NOT NULL,
    Quantity INTEGER NOT NULL
        CHECK(Quantity > 0),
    PurchaseDate DATE DEFAULT CURRENT_DATE,
    Supplier TEXT NOT NULL,
    Purchaseprice REAL NOT NULL
        CHECK(Purchaseprice >= 0),
    FOREIGN KEY(BookId) REFERENCES Books(BookId)
)
""")


# ==========================================
# BOOK PRICE HISTORY
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Bookpricehistory(
    HistoryId INTEGER PRIMARY KEY AUTOINCREMENT,
    BookId INTEGER,
    Oldprice REAL,
    Newprice REAL,
    Updatedate DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY(BookId) REFERENCES Books(BookId)
)
""")


# ==========================================
# AUDIT LOG
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Auditlog(
    LogId INTEGER PRIMARY KEY AUTOINCREMENT,
    Action TEXT NOT NULL,
    TableName TEXT NOT NULL,
    Record INTEGER NOT NULL,
    Description TEXT,
    ActionDate DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


# ==========================================
# TRIGGER: REDUCE AVAILABLE COPIES
# ==========================================

cursor.execute("""
CREATE TRIGGER IF NOT EXISTS reducecopies
AFTER INSERT ON Borrowing
WHEN (
    SELECT AvailableCopies
    FROM Books
    WHERE BookId = NEW.BookId
) > 0
BEGIN
    UPDATE Books
    SET AvailableCopies = AvailableCopies - 1
    WHERE BookId = NEW.BookId;
END
""")


# ==========================================
# TRIGGER: BOOK PRICE UPDATE
# ==========================================

cursor.execute("""
CREATE TRIGGER IF NOT EXISTS Bookpriceupdate
AFTER UPDATE OF Price ON Books
WHEN OLD.Price <> NEW.Price
BEGIN
    INSERT INTO Bookpricehistory
    (BookId, Oldprice, Newprice)
    VALUES
    (NEW.BookId, OLD.Price, NEW.Price);
END
""")


# ==========================================
# TRIGGER: MEMBER LOG
# ==========================================

cursor.execute("""
CREATE TRIGGER IF NOT EXISTS log_member
AFTER INSERT ON Members
BEGIN
    INSERT INTO Auditlog
    (Action, TableName, Record, Description)
    VALUES
    (
        'ADD_MEMBER',
        'Members',
        NEW.MemberId,
        'New member added'
    );
END
""")


# ==========================================
# TRIGGER: BORROWING LOG
# ==========================================

cursor.execute("""
CREATE TRIGGER IF NOT EXISTS log_borrowing
AFTER INSERT ON Borrowing
BEGIN
    INSERT INTO Auditlog
    (Action, TableName, Record, Description)
    VALUES
    (
        'ISSUE_BOOK',
        'Borrowing',
        NEW.BorrowId,
        'Book issued successfully'
    );
END
""")


# ==========================================
# TRIGGER: RETURN LOG
# ==========================================

cursor.execute("""
CREATE TRIGGER IF NOT EXISTS log_return
AFTER UPDATE OF ReturnDate ON Borrowing
WHEN NEW.ReturnDate IS NOT NULL
     AND OLD.ReturnDate IS NULL
BEGIN
    INSERT INTO Auditlog
    (Action, TableName, Record, Description)
    VALUES
    (
        'RETURN_BOOK',
        'Borrowing',
        NEW.BorrowId,
        'Book returned successfully'
    );
END
""")


# ==========================================
# TRIGGER: FINE PAYMENT LOG
# ==========================================

cursor.execute("""
CREATE TRIGGER IF NOT EXISTS fine_payment
AFTER UPDATE OF Paymentstatus ON Fines
WHEN NEW.Paymentstatus = 'Paid'
     AND OLD.Paymentstatus <> 'Paid'
BEGIN
    INSERT INTO Auditlog
    (Action, TableName, Record, Description)
    VALUES
    (
        'FINE_PAID',
        'Fines',
        NEW.FineID,
        'Fine payment completed'
    );
END
""")


# ==========================================
# VIEW: BORROW BOOK
# ==========================================

cursor.execute("DROP VIEW IF EXISTS BorrowBook")

cursor.execute("""
CREATE VIEW BorrowBook AS
SELECT
    b.BorrowId,
    m.MemberName,
    bk.BookTitle,
    b.BorrowDate,
    b.DueDate,
    b.ReturnDate,
    b.Status
FROM Borrowing b
JOIN Members m
    ON b.MemberId = m.MemberId
JOIN Books bk
    ON b.BookId = bk.BookId
""")


# ==========================================
# VIEW: RETURNED BOOKS
# ==========================================

cursor.execute("DROP VIEW IF EXISTS returnbooks")

cursor.execute("""
CREATE VIEW returnbooks AS
SELECT
    b.BorrowId,
    m.MemberName,
    bk.BookTitle,
    b.BorrowDate,
    b.DueDate,
    b.ReturnDate
FROM Borrowing b
JOIN Members m
    ON b.MemberId = m.MemberId
JOIN Books bk
    ON b.BookId = bk.BookId
WHERE b.Status = 'Returned'
""")


# ==========================================
# VIEW: AVAILABLE BOOKS
# ==========================================

cursor.execute("DROP VIEW IF EXISTS availablebooks")

cursor.execute("""
CREATE VIEW availablebooks AS
SELECT
    BookId,
    BookTitle,
    Author,
    Category,
    Quantity,
    AccessLevel,
    AvailableCopies,
    Price
FROM Books
WHERE AvailableCopies > 0
""")


# ==========================================
# VIEW: TEACHER BOOKS
# ==========================================

cursor.execute("DROP VIEW IF EXISTS teacherbooks")

cursor.execute("""
CREATE VIEW teacherbooks AS
SELECT *
FROM Books
WHERE AccessLevel = 'Teacher'
""")


# ==========================================
# VIEW: STUDENT BOOKS
# ==========================================

cursor.execute("DROP VIEW IF EXISTS studentbooks")

cursor.execute("""
CREATE VIEW studentbooks AS
SELECT *
FROM Books
WHERE AccessLevel = 'Student'
""")


# ==========================================
# VIEW: DUE FINES
# ==========================================

cursor.execute("DROP VIEW IF EXISTS duefines")

cursor.execute("""
CREATE VIEW duefines AS
SELECT
    FineID,
    BorrowId,
    Fineamount,
    Paymentstatus
FROM Fines
WHERE Paymentstatus = 'Due'
""")


# ==========================================
# VIEW: PURCHASE HISTORY
# ==========================================

cursor.execute("DROP VIEW IF EXISTS purchasehistory")

cursor.execute("""
CREATE VIEW purchasehistory AS
SELECT
    a.AcquisitionId,
    bk.BookTitle,
    a.Quantity,
    a.PurchaseDate,
    a.Supplier,
    a.Purchaseprice
FROM Acquisitions a
JOIN Books bk
    ON a.BookId = bk.BookId
""")


# ==========================================
# VIEW: BORROW SUMMARY
# ==========================================

cursor.execute("DROP VIEW IF EXISTS borrowsummary")

cursor.execute("""
CREATE VIEW borrowsummary AS
SELECT
    m.MemberId,
    m.MemberName,
    m.MemberType,
    COUNT(b.BorrowId) AS TotalBorrows
FROM Members m
LEFT JOIN Borrowing b
    ON m.MemberId = b.MemberId
GROUP BY
    m.MemberId,
    m.MemberName,
    m.MemberType
""")


# ==========================================
# DEFAULT USERS
# ==========================================

users = [
    ("5241411166", "student123", "Student"),
    ("6241411166", "teacher123", "Teacher"),
    ("22435-CSE-001", "admin123", "Admin")
]

for login_id, password, role in users:

    cursor.execute("""
        INSERT OR IGNORE INTO Users
        (LoginId, Password, Role)
        VALUES (?, ?, ?)
    """, (login_id, password, role))


# ==========================================
# DEFAULT MEMBERS
# ==========================================

members = [
    (
        "Dr. Kumar",
        "kumar@gmail.com",
        "9000000001",
        "Teacher",
        "6241411166"
    ),
    (
        "Rahul",
        "rahul@gmail.com",
        "9000000002",
        "Student",
        "5241411166"
    ),
    (
        "Priya",
        "priya@gmail.com",
        "9000000003",
        "Student",
        "5241411167"
    ),
    (
        "Sneha",
        "sneha@gmail.com",
        "9000000004",
        "Student",
        "5241411168"
    ),
    (
        "Prof. Ramesh",
        "ramesh@gmail.com",
        "9000000005",
        "Teacher",
        "6241411167"
    ),
    (
        "Anjali",
        "anjali@gmail.com",
        "9000000006",
        "Student",
        "5241411169"
    ),
    (
        "Arjun",
        "arjun@gmail.com",
        "9000000007",
        "Student",
        "5241411170"
    ),
    (
        "Dr. Meena",
        "meena@gmail.com",
        "9000000008",
        "Teacher",
        "6241411168"
    )
]

for member in members:

    cursor.execute("""
        INSERT OR IGNORE INTO Members
        (MemberName, Email, Phone, MemberType, LoginId)
        VALUES (?, ?, ?, ?, ?)
    """, member)


# ==========================================
# DEFAULT BOOKS
# ==========================================

books = [
    (
        "Python Programming",
        "Mark Lutz",
        "Programming",
        10,
        "Student",
        10,
        800
    ),
    (
        "Machine Learning",
        "Tom Mitchell",
        "AI",
        8,
        "Student",
        8,
        900
    ),
    (
        "Deep Learning",
        "Ian Goodfellow",
        "AI",
        5,
        "Teacher",
        5,
        1200
    ),
    (
        "Database System Concepts",
        "Korth",
        "Database",
        7,
        "Student",
        7,
        1000
    ),
    (
        "Computer Networks",
        "Andrew Tanenbaum",
        "Networking",
        6,
        "Student",
        6,
        950
    ),
    (
        "Operating System Concepts",
        "Silberschatz",
        "Operating System",
        5,
        "Teacher",
        5,
        1100
    ),
    (
        "Artificial Intelligence",
        "Stuart Russell",
        "AI",
        4,
        "Teacher",
        4,
        1300
    ),
    (
        "Data Structures",
        "Seymour Lipschutz",
        "Programming",
        10,
        "Student",
        10,
        700
    )
]

for book in books:

    cursor.execute("""
        INSERT OR IGNORE INTO Books
        (
            BookTitle,
            Author,
            Category,
            Quantity,
            AccessLevel,
            AvailableCopies,
            Price
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, book)

# ==========================================
# SAMPLE BORROWING DATA
# ==========================================

cursor.execute("""
SELECT MemberId
FROM Members
WHERE LoginId = ?
""", ("5241411166",))

student = cursor.fetchone()

cursor.execute("""
SELECT BookId
FROM Books
WHERE BookTitle = ?
""", ("Python Programming",))

python_book = cursor.fetchone()

if student and python_book:

    cursor.execute("""
    SELECT BorrowId
    FROM Borrowing
    WHERE MemberId = ? AND BookId = ?
    """, (student[0], python_book[0]))

    existing_borrow = cursor.fetchone()

    if not existing_borrow:

        cursor.execute("""
        INSERT INTO Borrowing
        (MemberId, BookId, BorrowDate, DueDate, Status)
        VALUES (?, ?, '2026-09-01', '2026-09-05', 'Returned')
        """, (student[0], python_book[0]))

        borrow_id = cursor.lastrowid

        cursor.execute("""
        UPDATE Books
        SET AvailableCopies = AvailableCopies + 1
        WHERE BookId = ?
        """, (python_book[0],))

        cursor.execute("""
        UPDATE Borrowing
        SET ReturnDate = '2026-09-10'
        WHERE BorrowId = ?
        """, (borrow_id,))

        # Add a sample fine
        cursor.execute("""
        INSERT INTO Fines
        (BorrowId, Fineamount, Paymentstatus)
        VALUES (?, 50, 'Due')
        """, (borrow_id,))
# ==========================================
# COMMIT CHANGES
# ==========================================

connection.commit()

print("Database initialized successfully!")

connection.close()