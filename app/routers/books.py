from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from .. import models, schemas
from ..database import get_db
from .auth import check_admin_access

router = APIRouter(tags=["books"], prefix="/books")

@router.get("/", response_model=List[schemas.BookOut])
async def list_books(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    title: Optional[str] = None,
    author: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Book)
    
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(models.Book.author.ilike(f"%{author}%"))
    
    books = query.offset(skip).limit(limit).all()
    return books

@router.post("/", response_model=schemas.BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_admin_access)
):
    db_book = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if db_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this ISBN already exists"
        )
    
    db_book = models.Book(
        title=book.title,
        author=book.author,
        published_date=book.published_date,
        isbn=book.isbn,
        total_copies=book.total_copies,
        available_copies=book.total_copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.get("/{book_id}", response_model=schemas.BookOut)
async def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

@router.put("/{book_id}", response_model=schemas.BookOut)
async def update_book(
    book_id: int,
    book_update: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_admin_access)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book_update.isbn != db_book.isbn:
        existing_book = db.query(models.Book).filter(models.Book.isbn == book_update.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists"
            )
    
    for var, value in vars(book_update).items():
        setattr(db_book, var, value)
    
    if book_update.total_copies != db_book.total_copies:
        borrowed_copies = db_book.total_copies - db_book.available_copies
        db_book.available_copies = max(0, book_update.total_copies - borrowed_copies)
    
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_admin_access)
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    active_borrowings = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.book_id == book_id,
        models.BorrowedBook.return_date.is_(None)
    ).first()
    
    if active_borrowings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete book with active borrowings"
        )
    
    db.delete(db_book)
    db.commit()
    return None
