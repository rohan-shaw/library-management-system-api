from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime, date
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class BookBase(BaseModel):
    title: str
    author: str
    published_date: Optional[date]
    isbn: str = Field(..., pattern="^(97(8|9))?\\d{9}(\\d|X)$")
    total_copies: int

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str]
    author: Optional[str]
    published_date: Optional[date]
    isbn: Optional[str] = Field(..., pattern="^(97(8|9))?\\d{9}(\\d|X)$")
    available_copies: Optional[int]
    total_copies: Optional[int]

    class Config:
        orm_mode = True

class BookOut(BookBase):
    id: int
    available_copies: int

    class Config:
        orm_mode = True

class BorrowedBookBase(BaseModel):
    book_id: int

class BorrowedBookCreate(BorrowedBookBase):
    pass

class BorrowedBookOut(BorrowedBookBase):
    id: int
    user_id: int
    borrow_date: datetime
    return_date: Optional[datetime]

    class Config:
        orm_mode = True

class BorrowedBookWithDetails(BorrowedBookOut):
    book: BookOut

    class Config:
        orm_mode = True


class UserWithStats(UserOut):
    total_books_borrowed: int
    active_borrowings: int
    overdue_borrowings: int

    class Config:
        orm_mode = True

class BorrowingHistory(BorrowedBookOut):
    user: UserOut
    book: BookOut
    duration_days: Optional[float]
    is_overdue: bool

    class Config:
        orm_mode = True