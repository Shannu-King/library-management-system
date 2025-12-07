# Library Management System API

## Setup Instructions
1. Clone the repo.
2. Run `pip install -r requirements.txt`.
3. Run `uvicorn main:app --reload`.
4. Open `http://127.0.0.1:8000/docs` to test.

## Features
* **Books:** Track stock and status (Available/Borrowed).
* **Transactions:** Enforce max 3 books per user.
* **Fines:** Calculate $0.50/day for overdue books.