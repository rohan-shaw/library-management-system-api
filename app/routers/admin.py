from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, aliased
from typing import List, Optional
import datetime

from .. import models, schemas
from ..database import get_db
from .auth import check_admin_access

router = APIRouter(tags=["admin"], prefix="/admin")

@router.get("/users", response_model=List[schemas.UserWithStats])
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_admin_access)
):
    query = db.query(models.User)
    
    if active_only:
        query = query.filter(models.User.is_active == True)
    
    users = query.offset(skip).limit(limit).all()
    
    users_with_stats = []
    for user in users:
        total_borrowed = db.query(models.BorrowedBook).filter(
            models.BorrowedBook.user_id == user.id
        ).count()
        
        active_borrowings = db.query(models.BorrowedBook).filter(
            models.BorrowedBook.user_id == user.id,
            models.BorrowedBook.return_date.is_(None)
        ).count()
        
        overdue_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)
        overdue_borrowings = db.query(models.BorrowedBook).filter(
            models.BorrowedBook.user_id == user.id,
            models.BorrowedBook.return_date.is_(None),
            models.BorrowedBook.borrow_date < overdue_date
        ).count()
        
        user_dict = {
            **user.__dict__,
            'total_books_borrowed': total_borrowed,
            'active_borrowings': active_borrowings,
            'overdue_borrowings': overdue_borrowings
        }
        users_with_stats.append(user_dict)
    
    return users_with_stats

@router.get("/borrowing-history", response_model=List[schemas.BorrowingHistory])
async def get_borrowing_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user_id: Optional[int] = None,
    book_id: Optional[int] = None,
    active_only: bool = False,
    overdue_only: bool = False,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_admin_access)
):
    UserAlias = aliased(models.User)
    BookAlias = aliased(models.Book)

    query = (
        db.query(
            models.BorrowedBook,
            UserAlias,
            BookAlias
        )
        .join(UserAlias, models.BorrowedBook.user_id == UserAlias.id)  
        .join(BookAlias, models.BorrowedBook.book_id == BookAlias.id)
    )

    if user_id:
        query = query.filter(models.BorrowedBook.user_id == user_id)
    if book_id:
        query = query.filter(models.BorrowedBook.book_id == book_id)
    if active_only:
        query = query.filter(models.BorrowedBook.return_date.is_(None))
    if start_date:
        query = query.filter(models.BorrowedBook.borrow_date >= start_date)
    if end_date:
        query = query.filter(models.BorrowedBook.borrow_date <= end_date)
    if overdue_only:
        overdue_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)
        query = query.filter(
            models.BorrowedBook.return_date.is_(None),
            models.BorrowedBook.borrow_date < overdue_date
        )

    query = query.order_by(models.BorrowedBook.borrow_date.desc())

    borrowings = query.offset(skip).limit(limit).all()

    result = []
    for borrowing, user, book in borrowings:
        if borrowing.return_date:
            duration = (borrowing.return_date - borrowing.borrow_date).total_seconds() / 86400
            is_overdue = duration > 14
        else:
            duration = (datetime.datetime.now().replace(tzinfo=None) - borrowing.borrow_date).total_seconds() / 86400
            is_overdue = duration > 14

        borrowing_dict = schemas.BorrowingHistory(
            id=borrowing.id,
            user_id=borrowing.user_id,  
            book_id=borrowing.book_id, 
            user=schemas.UserOut.model_validate(user.__dict__),  
            book=schemas.BookOut.model_validate(book.__dict__), 
            borrow_date=borrowing.borrow_date,
            return_date=borrowing.return_date,
            duration_days=round(duration, 2),
            is_overdue=is_overdue
        )
        result.append(borrowing_dict)

    return result