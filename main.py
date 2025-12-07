from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud, database

# This command creates the database tables automatically when the app starts
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Library Management System API")

# Dependency to get the Database Session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- BOOK ENDPOINTS ---
@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db=db, book=book)

@app.get("/books/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_books(db, skip=skip, limit=limit)

# --- MEMBER ENDPOINTS ---
@app.post("/members/", response_model=schemas.Member)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    return crud.create_member(db=db, member=member)

# --- TRANSACTION ENDPOINTS ---
@app.post("/transactions/borrow", response_model=schemas.Transaction)
def borrow_book(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, transaction=transaction)

@app.post("/transactions/return/{transaction_id}", response_model=schemas.Transaction)
def return_book(transaction_id: int, db: Session = Depends(get_db)):
    return crud.return_book(db=db, transaction_id=transaction_id)
    # --- NEW: REPORTING ENDPOINTS ---

@app.get("/books/available", response_model=List[schemas.Book])
def read_available_books(db: Session = Depends(get_db)):
    return crud.get_available_books(db)

@app.get("/transactions/overdue", response_model=List[schemas.Transaction])
def read_overdue_transactions(db: Session = Depends(get_db)):
    return crud.get_overdue_transactions(db)

@app.post("/fines/{fine_id}/pay")
def pay_fine(fine_id: int, db: Session = Depends(get_db)):
    return crud.pay_fine(db, fine_id=fine_id)