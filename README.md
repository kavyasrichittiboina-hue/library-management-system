# Library Management System

A web-based Library Management System developed using Python, Flask, SQLite, HTML, CSS, and JavaScript.

## Features

### User Features
- User login
- Student and Teacher roles
- View available books
- View personal borrowing history
- View personal fines

### Admin Features
- Admin login
- Manage library members
- Add new books
- Add new copies
- Update book prices
- Issue books
- Return books
- Manage fines
- Record fine payments
- Manage acquisitions
- View book price history
- View audit logs
- Generate library reports

## Library Rules

- Only Admin can issue books.
- Only Admin can return books.
- Students can borrow a maximum of 3 active books.
- Students cannot borrow Teacher-only books.
- Teachers can borrow available books.
- Members with unpaid fines cannot be issued another book.
- Book availability is automatically updated when books are issued.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Jinja2

## Database

The system uses SQLite for storing:

- Books
- Members
- Users
- Borrowing
- Fines
- Acquisitions
- Book Price History
- Audit Logs

## Project Structure

```text
LibraryManagementSystem/
│
├── app.py
├── database.py
├── create_users.py
├── README.md
│
├── ERDiagram/
│   └── library.drawio
│
├── ProjectDocumentation/
│   └── Library_Management_System_Documentation.docx
│
├── static/
│   └── style.css
│
└── templates/
    ├── base.html
    ├── login.html
    ├── admin_dashboard.html
    ├── user_dashboard.html
    ├── books.html
    ├── members.html
    ├── borrowing.html
    ├── fines.html
    └── ...
