from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import BookStatus, MemberStatus, TransactionStatus

# --- BOOK SCHEMAS ---
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    available_copies: int
    status: BookStatus
    
    class Config:
        from_attributes = True

# --- MEMBER SCHEMAS ---
class MemberBase(BaseModel):
    name: str
    email: str
    membership_number: str

class MemberCreate(MemberBase):
    pass

class Member(MemberBase):
    id: int
    status: MemberStatus

    class Config:
        from_attributes = True

# --- TRANSACTION SCHEMAS ---
class TransactionCreate(BaseModel):
    book_id: int
    member_id: int

class Transaction(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrowed_at: datetime
    due_date: datetime
    returned_at: Optional[datetime] = None
    status: TransactionStatus

    class Config:
        from_attributes = True