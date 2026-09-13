import sqlite3
#connect database
connection=sqlite3.connect("library.db")
print("Database connect successfully")
cursor=connection.cursor()
#Member tables
cursor.execute("""create table if not exists Members(MemberId integer primary key autoincrement, MemberName text not null,
Email text unique,Phone text, MemberType text not null check(MemberType in('Teacher','Student')),JoinDate date default current_date,Status text default 'Active');""")
print("Members table created successfully")
cursor.execute("""
ALTER TABLE Members
ADD COLUMN LoginId TEXT
""")

cursor.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS
idx_members_loginid
ON Members(LoginId)
""")

#insert data member table
'''cursor.execute("""insert into Members(MemberName,Email,Phone,MemberType) values 
('Dr. Kumar', 'kumar@gmail.com', '9876543211', 'Teacher'),
('Rahul', 'rahul@gmail.com', '9876543212', 'Student'),
('Priya', 'priya@gmail.com', '9876543213', 'Student'),
('Sneha', 'sneha@gmail.com', '9876543214', 'Student'),
('Prof. Ramesh', 'ramesh@gmail.com', '9876543215', 'Teacher'),
('Anjali', 'anjali@gmail.com', '9876543216', 'Student'),
('Arjun', 'arjun@gmail.com', '9876543217', 'Student'),
('Dr. Meena', 'meena@gmail.com', '9876543218', 'Teacher');""")
print("Members saved successfully.")'''

#Books table
cursor.execute("""create table if not exists Books(BookId integer primary key autoincrement,BookTitle text not null,
Author text not null,Category text,Quantity integer not null default 0, AccessLevel text not null check(AccessLevel in('Teacher','Student')),AvailableCopies integer not null default 0,Price real);""")
cursor.execute("""
insert into Books
(BookTitle, Author, Category, Quantity, AccessLevel, AvailableCopies, Price)
values
('Python Programming', 'John Smith', 'Programming', 10, 'Student', 10, 499),
('Database Systems', 'Navathe', 'Database', 5, 'Student', 5, 650),
('Artificial Intelligence', 'Russell & Norvig', 'AI', 4, 'Teacher', 4, 1200),
('Machine Learning', 'Tom Mitchell', 'AI', 3, 'Teacher', 3, 1500),
('Data Structures', 'Mark Allen', 'Programming', 8, 'Student', 8, 700),
('Operating Systems', 'Silberschatz', 'Computer Science', 6, 'Student', 6, 900),
('Computer Networks', 'Andrew Tanenbaum', 'Networking', 5, 'Student', 5, 850),
('Deep Learning', 'Ian Goodfellow', 'AI', 2, 'Teacher', 2, 1800);
""")
print("Books saved successfully.")

cursor.execute("""create table if not exists Users(UserId integer primary key autoincrement,
LoginId text unique not null,Password text not null,Role text not null)""")
cursor.execute("""insert or ignore into Users(LoginId,Password,Role) values""",("5241411166","student123","Student"))
cursor.execute("""
INSERT OR IGNORE INTO Users
(LoginId, Password, Role)
VALUES (?, ?, ?)
""", (
    "6241411166",
    "teacher123",
    "Teacher"
))


cursor.execute("""
INSERT OR IGNORE INTO Users
(LoginId, Password, Role)
VALUES (?, ?, ?)
""", (
    "22435-CSE-001",
    "admin123",
    "Admin"
))

#Borrowing table
cursor.execute("""create table if not exists Borrowing(BorrowId integer primary key autoincrement,MemberId integer not null,
BookId integer not null,BorrowDate date default current_date,DueDate date not null,ReturnDate date, Status text default 'Borrowed' check(Status in ('Borrowed','Returned')),
foreign key(MemberId) references Members(MemberId), foreign key(BookId) references Books (BookId));""")
# Reduce Available Copies after issuing
cursor.execute("""
CREATE TRIGGER IF NOT EXISTS reducecopies
AFTER INSERT ON Borrowing
WHEN (SELECT AvailableCopies FROM Books WHERE BookId = NEW.BookId) > 0
BEGIN
    UPDATE Books
    SET AvailableCopies = AvailableCopies - 1
    WHERE BookId = NEW.BookId;
END;
""")
cursor.execute("""insert into Borrowing (MemberID, BookID, DueDate)values
(2,1,'2026-08-10'),
(2,2,'2026-08-12'),
(3,5,'2026-08-15'),
(4,6,'2026-08-18'),
(1,3,'2026-08-20'),
(5,4,'2026-08-22'),
(6,7,'2026-08-25'),
(7,1,'2026-08-27');""")
print("Borrowing saved successfully.")
cursor.execute("""
UPDATE Borrowing
SET Status = 'Returned',ReturnDate = CURRENT_DATE
WHERE BorrowId = 1;""")

cursor.execute("""
UPDATE Books
SET AvailableCopies = AvailableCopies + 1
WHERE BookId = (SELECT BookId FROM Borrowing WHERE BorrowId = 1
);""")

#Fines table
cursor.execute("""create table if not exists Fines(FineID integer primary key autoincrement,BorrowId integer,
Fineamount real,Paymentstatus text not null check(Paymentstatus in('Paid','Due')), foreign key(BorrowId) references Borrowing (BorrowId));""")
cursor.execute("""
INSERT INTO Fines (BorrowId, FineAmount, PaymentStatus)
VALUES
(1,50,'Due'),
(2,0,'Paid'),
(3,100,'Due'),
(5,25,'Paid');
""")
print("Fines table saved successfully.")

#Acquisitions
cursor.execute("""create table if not exists Acquisitions(AcquisitionId integer primary key autoincrement,BookId integer not null,Quantity integer not null check(Quantity>0),PurchaseDate date default current_date,Supplier text not null,
Purchaseprice real not null check(Purchaseprice >=0),foreign key(BookId) references Books(BookId));""")
cursor.execute("""
INSERT INTO Acquisitions
(BookId, Quantity, PurchaseDate, Supplier, PurchasePrice)
VALUES
(1,5,'2026-07-01','ABC Book Suppliers',2500),
(2,3,'2026-07-05','National Book House',1950),
(3,2,'2026-07-10','Research Publications',2400),
(4,2,'2026-07-12','AI Publications',3000),
(5,4,'2026-07-15','Tech Books Pvt Ltd',2800),
(6,3,'2026-07-18','Academic Books',2700),
(7,2,'2026-07-20','Knowledge World',1700),
(8,1,'2026-07-25','Deep Learning Press',1800);
""")
print("Acquisitions saved successfully.")

#BookPriceHistory
cursor.execute("""create table if not exists Bookpricehistory(HistoryId integer primary key autoincrement,BookId integer,
Oldprice real,Newprice real,Updatedate date default current_date,foreign key(BookId) references Books(BookId));""")
cursor.execute("""insert into Bookpricehistory(BookId,Oldprice,Newprice) values
(1,450,499),
(2,600,650),
(3,1100,1200),
(4,1400,1500),
(5,650,700),
(6,850,900),
(7,800,850),
(8,1700,1800);""")
print("BookPriceHistory saved successfully.")


#AuditLog
cursor.execute("""create table if not exists Auditlog(LogId integer primary key autoincrement,Action text not null,
TableName text not null,Record integer not null,Description text,ActionDate datetime default current_timestamp);""")
cursor.execute("""insert into Auditlog(Action,TableName,Record,Description) values
('INSERT','Members',1,'Teacher registered'),
('INSERT','Books',3,'Artificial Intelligence book added'),
('ISSUE_BOOK','Borrowing',1,'Python Programming issued to Rahul'),
('ISSUE_BOOK','Borrowing',5,'Artificial Intelligence issued to Dr. Kumar'),
('RETURN_BOOK','Borrowing',2,'Database Systems returned'),
('FINE_CREATED','Fines',1,'Late return fine created'),
('FINE_PAID','Fines',2,'Fine payment completed'),
('PRICE_UPDATED','Books',3,'Book price updated');""")

print("AuditLog saved successfully.")


cursor.execute("""select count(*) as Totalbooks from Borrowing where MemberId=2 and Status='Borrowed';""")


cursor.execute("""select MemberType from Members where MemberId=1;""")

cursor.execute("""select AccessLevel from Books where BookId=4""")

cursor.execute("""select * from Members where MemberId=1;""")

cursor.execute("""select Status from Members where MemberId=1""")

cursor.execute("""SELECT *
FROM Fines
WHERE BorrowId IN (
    SELECT BorrowId
    FROM Borrowing
    WHERE MemberId = 1
)
AND PaymentStatus = 'Due';""")

cursor.execute("""SELECT COUNT(*) AS TotalBorrowed
FROM Borrowing
WHERE MemberID=1
AND Status='Borrowed';""")



cursor.execute("""SELECT
BorrowId,
DueDate,
ReturnDate
FROM Borrowing
WHERE BorrowId = 1;""")

cursor.execute("""select * from Bookpricehistory;""")

cursor.execute("""select m.MemberId,m.MemberName,b.BookTitle,br.BorrowDate,br.DueDate,br.Status
 from Members m inner join Borrowing br on m.MemberId=br.MemberId inner join Books b on br.BookId=b.BookId;""")

#show which member borrowed which book
cursor.execute("""select m.MemberId,m.MemberName,b.BookTitle,f.Fineamount,f.Paymentstatus from Members m inner join Borrowing br on
m.MemberId=br.MemberId inner join Books b on b.BookId=br.BookId  inner join Fines f on br.BorrowId=f.BorrowId where f.Paymentstatus='Due'; """)

#Members with Unpaid Fines
cursor.execute("""select m.MemberName,b.BookTitle,f.Fineamount,f.Paymentstatus from Members m inner join Borrowing br
on m.MemberId=br.MemberId inner join Books b on br.BookId=b.BookId inner join Fines f on br.BorrowId=f.BorrowId where f.Paymentstatus='Due';""")

#Teacher Books
cursor.execute("""select BookTitle,Author,Price from Books where AccessLevel='Teacher';""")

#Student Books
cursor.execute("""select BookTitle,Author,Price from Books where AccessLevel='Student';""")

#Available Copies
cursor.execute("""select BookTitle,AvailableCopies from Books where AvailableCopies>0;""")

#Books Currently Borrowed
cursor.execute("""select m.MemberName,b.BookTitle,br.BorrowDate,br.DueDate from Members m inner join Borrowing br on m.MemberId=br.MemberId 
inner join Books b on b.BookId=br.BookId where br.Status='Borrowed';""")

#Returned Books
cursor.execute("""select m.MemberName,b.BookTitle,br.BorrowDate,br.DueDate,br.ReturnDate from Members m inner join Borrowing br
on m.MemberId=br.MemberId inner join  Books b on b.BookId=br.BookId where br.Status='Returned';""")

#Books Purchased
cursor.execute("""select b.BookTitle,b.Quantity,b.AvailableCopies,a.Purchaseprice,a.Supplier from Books b join Acquisitions a
where b.BookId=a.BookId; """)

#price change
cursor.execute("""select b.BookTitle,p.Oldprice,p.Newprice from Books b join 
Bookpricehistory p on b.BookId=p.BookId;""")

#Borrow count per member
cursor.execute("""select m.MemberName,count(br.BorrowId) as TotalBorrowed from Members 
m left join Borrowing br on m.MemberId=br.MemberId group by m.MemberId,m.MemberName;""")

#Borrow count per Book
cursor.execute("""select b.BookTitle,count(br.BookId) as BorrowedBooks from Books b left join 
Borrowing br where b.BookId=br.BookId group by b.BookId,b.BookTitle;""")

#Members who Borrowed Teacher Books
cursor.execute("""select m.MemberName,b.BookTitle,b.AccessLevel from Members m join Borrowing br on m.MemberId=br.MemberId 
join Books b on br.BookId=b.BookId where AccessLevel='Teacher';""")

#Students Who Borrowed 3 or More Books
cursor.execute("""select m.MemberName,count(br.BorrowId) as TotalBooks from Members m join Borrowing br on
m.MemberId=br.MemberId where m.MemberType='Student' group by m.MemberId,m.MemberName having count(br.BorrowId)>=3;""")

#Members with No borrowings
cursor.execute("""select m.MemberName from Members m left join Borrowing br on m.MemberId=br.MemberId where br.MemberId is NULL;""")

#Current Borrowed Books view
cursor.execute("""drop view if exists BorrowBook;""")
cursor.execute("""create view BorrowBook as select m.MemberName,br.BorrowId,b.BookTitle,br.BorrowDate,br.DueDate from Borrowing br join Members m on br.MemberId=m.MemberId join Books b on b.BookId=br.BookId where br.Status='Borrowed';""")
cursor.execute("""select * from BorrowBook;""")


#Returned Books
cursor.execute("""drop view if exists returnbooks;""")
cursor.execute("""create view returnbooks as select m.MemberName,br.BorrowId, b.BookTitle,br.ReturnDate from Members m join Borrowing br on m.MemberId=br.MemberId join Books b on b.BookId=br.BookId where br.Status='Returned';""")
cursor.execute("""select * from returnbooks;""")

#Available Books
cursor.execute("""drop view if exists availablebooks;""")
cursor.execute("""create view availablebooks as select BookId,BookTitle,Author,AvailableCopies from Books where AvailableCopies>0;""")
cursor.execute("""select * from availablebooks""")

#Teacher Books
cursor.execute("""drop view if exists teacherbooks;""")
cursor.execute("""create view teacherbooks as select BookId,BookTitle,Author,Price from Books where AccessLevel='Teacher'; """)
cursor.execute("""select * from teacherbooks;""")

#Student Books
cursor.execute("""drop view if exists studentbooks;""")
cursor.execute("""create view studentbooks as select BookId,BookTitle,Author,Price from Books where AccessLevel='Teacher'; """)
cursor.execute("""select * from studentbooks;""")

#Members with fines
cursor.execute("""drop view if exists duefines;""")
cursor.execute("""create view duefines as select m.MemberName,
b.BookTitle,f.Fineamount from Members m join Borrowing br on 
m.MemberId=br.MemberId join Books b on br.BookId=b.BookId join Fines
 f on br.BorrowId=f.BorrowId where f.PaymentStatus='Due';""")
cursor.execute("""select * from duefines;""")

#Book Purchase History
cursor.execute("""drop view if exists purchasehistory;""")
cursor.execute("""create view purchasehistory as select b.BookTitle,a.Supplier,a.Quantity,a.PurchaseDate from Books b join Acquisitions a on b.BookId=a.BookId;""")
cursor.execute("""select * from purchasehistory;""")

cursor.execute("""drop view if exists borrowsummary;""")
cursor.execute("""create view borrowsummary as select m.MemberId,m.MemberName,count(br.BorrowId) as TotalBorrowed from Members m join Borrowing br
on m.MemberId=br.MemberId group by m.MemberId,m.MemberName;""")
cursor.execute("""select * from borrowsummary;""")

# Check Available Copies
cursor.execute("""
SELECT BookTitle, Quantity, AvailableCopies
FROM Books
WHERE BookId = 1;""")
result = cursor.fetchall()
print(result)


# Book Price History Trigger
cursor.execute("""
CREATE TRIGGER IF NOT EXISTS Bookpriceupdate 
AFTER UPDATE OF Price ON Books 
WHEN OLD.Price <> NEW.Price
BEGIN 
    INSERT INTO Bookpricehistory
    (
        BookId,
        Oldprice,
        Newprice,
        Updatedate
    )
    VALUES
    (
        OLD.BookId,
        OLD.Price,
        NEW.Price,
        CURRENT_DATE
    ); 
END;
""")


#Audit Log-New member
cursor.execute("""Create Trigger if not exists log_member after insert on Members begin
insert into AuditLog(Action,TableName,Record,Description) values('Insert','Members',new.MemberId,'New member registered:'||new.MemberName); end;""")

#log_borrowing
cursor.execute("""create trigger if not exists log_return after update of ReturnDate on Borrowing when new.ReturnDate is not null and old.ReturnDate is null begin
insert into AuditLog(Action,TableName,Record,Description)values('RETURN_BOOK','Borrowing',NEW.BorrowId,'Book return successfully'); end;""")
#fine payment status
cursor.execute("""create trigger if not exists fine_payment after update of PaymentStatus on Fines when new.PaymentStatus='Paid' and old.PaymentStatus<>'Paid' begin
insert into AuditLog(Action,TableName,Record,Description) values('PAY_FINES','FINES',NEW.FineId,'Fine Paid Successfully');end;""")
#report
cursor.execute("""select count(*) as TotalBooks,sum(Quantity) as TotalCopies, sum(AvailableCopies) as AvailableCopies, sum(Quantity-AvailableCopies) as BorrowedCopies from Books;""")
summary=cursor.fetchone()
print("\n===== LIBRARY SUMMARY =====")
print("Total Books:", summary[0])
print("Total Copies:", summary[1])
print("Available Copies:", summary[2])
print("Borrowed Copies:", summary[3])

#Borrowed books report
cursor.execute("""select Borrowing.BorrowId,Members.MemberName,Books.BookTitle,Borrowing.BorrowDate,Borrowing.DueDate,Borrowing.Status from Borrowing 
join Members on Borrowing.MemberId=Members.MemberId join Books on
Borrowing.BookId=Books.BookId where Borrowing.Status='Borrowed' order by Borrowing.BorrowDate;""")
borrowed_books=cursor.fetchall()
print("\n ===BORROWED BOOKS REPORT===")
for row in borrowed_books:
    print(row)


# Save changes
connection.commit()
# Close database
connection.close()

print("Database connection closed successfully")





