from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

# Define Enums (Choices for status)
class BookStatus(str, enum.Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"

class MemberStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

class TransactionStatus(str, enum.Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"

# Define Tables
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    isbn = Column(String, unique=True, index=True)
    category = Column(String)
    status = Column(Enum(BookStatus), default=BookStatus.AVAILABLE)
    total_copies = Column(Integer)
    available_copies = Column(Integer)

    transactions = relationship("Transaction", back_populates="book")

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    membership_number = Column(String, unique=True)
    status = Column(Enum(MemberStatus), default=MemberStatus.ACTIVE)

    transactions = relationship("Transaction", back_populates="member")
    fines = relationship("Fine", back_populates="member")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    member_id = Column(Integer, ForeignKey("members.id"))
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    returned_at = Column(DateTime, nullable=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.ACTIVE)

    book = relationship("Book", back_populates="transactions")
    member = relationship("Member", back_populates="transactions")
    fine = relationship("Fine", back_populates="transaction", uselist=False)

class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    amount = Column(Float)
    paid_at = Column(DateTime, nullable=True)

    member = relationship("Member", back_populates="fines")
    transaction = relationship("Transaction", back_populates="fine")