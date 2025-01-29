from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    is_admin = Column(Boolean, default=False)
    
    borrowed_books = relationship("BorrowedBook", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    published_date = Column(Date)
    isbn = Column(String, unique=True)
    available_copies = Column(Integer)
    total_copies = Column(Integer)

    borrowed_records = relationship("BorrowedBook", back_populates="book")

class BorrowedBook(Base):
    __tablename__ = "borrowed_books"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    borrow_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_records")