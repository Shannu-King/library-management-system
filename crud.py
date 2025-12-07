from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException
import models, schemas

# --- BOOK OPERATIONS ---
def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def create_book(db: Session, book: schemas.BookCreate):
    # Convert Pydantic model to dict
    book_data = book.dict()
    # Logic: Initially, available copies = total copies
    db_book = models.Book(
        **book_data, 
        available_copies=book.total_copies,
        status=models.BookStatus.AVAILABLE
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# --- MEMBER OPERATIONS ---
def create_member(db: Session, member: schemas.MemberCreate):
    db_member = models.Member(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_member(db: Session, member_id: int):
    return db.query(models.Member).filter(models.Member.id == member_id).first()

# --- TRANSACTION (BORROW) LOGIC ---
def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    # 1. Fetch Entities
    book = get_book(db, transaction.book_id)
    member = get_member(db, transaction.member_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # 2. RULE: Member Suspended?
    if member.status == models.MemberStatus.SUSPENDED:
        raise HTTPException(status_code=400, detail="Member is suspended")

    # 3. RULE: Unpaid Fines?
    # Check if member has any fines where paid_at is None
    unpaid_fine = db.query(models.Fine).filter(
        models.Fine.member_id == member.id, 
        models.Fine.paid_at == None
    ).first()
    if unpaid_fine:
        raise HTTPException(status_code=400, detail="Member has unpaid fines. Cannot borrow.")

    # 4. RULE: Borrow Limit (Max 3)
    active_loans = db.query(models.Transaction).filter(
        models.Transaction.member_id == member.id,
        models.Transaction.status == models.TransactionStatus.ACTIVE
    ).count()
    if active_loans >= 3:
        raise HTTPException(status_code=400, detail="Borrowing limit reached (Max 3 books)")

    # 5. RULE: Book Availability
    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="Book not available")

    # 6. ACTION: Create Transaction
    # Due date is 14 days from now
    due_date = datetime.utcnow() + timedelta(days=14)
    db_txn = models.Transaction(
        book_id=book.id,
        member_id=member.id,
        due_date=due_date,
        status=models.TransactionStatus.ACTIVE
    )
    
    # 7. ACTION: Update Book State
    book.available_copies -= 1
    if book.available_copies == 0:
        book.status = models.BookStatus.BORROWED
        
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn

# --- TRANSACTION (RETURN) LOGIC ---
def return_book(db: Session, transaction_id: int):
    txn = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn.status == models.TransactionStatus.RETURNED:
        raise HTTPException(status_code=400, detail="Book already returned")
        
    member = txn.member
    book = txn.book
    
    # 1. Calculate Overdue Fine
    now = datetime.utcnow()
    # If now is after due_date
    if now > txn.due_date:
        overdue_days = (now - txn.due_date).days
        if overdue_days > 0:
            fine_amount = overdue_days * 0.50 # $0.50 per day
            new_fine = models.Fine(
                member_id=member.id,
                transaction_id=txn.id,
                amount=fine_amount
            )
            db.add(new_fine)
            # Mark transaction as Overdue internally before closing (optional logic)
            # But we are returning it now, so we just add the fine.
            
    # 2. Update Transaction
    txn.returned_at = now
    txn.status = models.TransactionStatus.RETURNED
    
    # 3. Update Book State
    book.available_copies += 1
    # If book was borrowed/out of stock, it is now available
    if book.status == models.BookStatus.BORROWED:
        book.status = models.BookStatus.AVAILABLE
        
    db.commit()
    db.refresh(txn)
    return txn
    # --- NEW: REPORTING & FINES LOGIC ---

def get_available_books(db: Session):
    # Return only books where available_copies > 0
    return db.query(models.Book).filter(models.Book.available_copies > 0).all()

def get_overdue_transactions(db: Session):
    # Return transactions that are ACTIVE and past their due date
    now = datetime.utcnow()
    return db.query(models.Transaction).filter(
        models.Transaction.status == models.TransactionStatus.ACTIVE,
        models.Transaction.due_date < now
    ).all()

def pay_fine(db: Session, fine_id: int):
    fine = db.query(models.Fine).filter(models.Fine.id == fine_id).first()
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    if fine.paid_at:
        raise HTTPException(status_code=400, detail="Fine already paid")
    
    # Mark as paid
    fine.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(fine)
    return {"message": "Fine paid successfully", "fine_id": fine.id, "amount": fine.amount}