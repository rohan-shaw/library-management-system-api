from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import datetime

from .. import models, schemas
from ..database import get_db
from .auth import get_current_active_user

router = APIRouter(tags=["borrowing"])

@router.post("/borrow/{book_id}", response_model=schemas.BorrowedBookOut)
async def borrow_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
): 
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No copies available for borrowing"
        )
    
    existing_borrow = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.user_id == current_user.id,
        models.BorrowedBook.book_id == book_id,
        models.BorrowedBook.return_date.is_(None)
    ).first()
    
    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active borrowing for this book"
        )
    
    borrowed_book = models.BorrowedBook(
        user_id=current_user.id,
        book_id=book_id,
        borrow_date=datetime.datetime.now(datetime.timezone.utc)
    )
    
    book.available_copies -= 1
    
    db.add(borrowed_book)
    db.commit()
    db.refresh(borrowed_book)
    
    return borrowed_book

@router.post("/return/{book_id}", response_model=schemas.BorrowedBookOut)
async def return_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    borrowed_book = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.user_id == current_user.id,
        models.BorrowedBook.book_id == book_id,
        models.BorrowedBook.return_date.is_(None)
    ).first()
    
    if not borrowed_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active borrowing found for this book"
        )
    
    borrowed_book.return_date = datetime.datetime.now(datetime.timezone.utc)
    
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    book.available_copies += 1
    
    db.commit()
    db.refresh(borrowed_book)
    
    return borrowed_book

@router.get("/borrowed", response_model=List[schemas.BorrowedBookOut])
async def get_user_borrowed_books(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    borrowed_books = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.user_id == current_user.id
    ).order_by(models.BorrowedBook.borrow_date.desc()).all()
    
    return borrowed_books

@router.get("/borrowed/details", response_model=List[schemas.BorrowedBookWithDetails])
async def get_user_borrowed_books_with_details(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    borrowed_books = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.user_id == current_user.id
    ).order_by(
        models.BorrowedBook.return_date.is_(None).desc(),
        models.BorrowedBook.borrow_date.desc()
    ).all()
    
    return borrowed_books