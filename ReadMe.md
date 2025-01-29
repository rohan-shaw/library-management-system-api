# Library Management System

A RESTful API for managing library operations built with FastAPI and PostgreSQL, featuring JWT authentication, CRUD operations, and admin functionalities.

## Features

- JWT-based user authentication
- Book management (CRUD operations)
- Book borrowing/returning system
- Admin dashboard for user and borrowing history management
- Request logging middleware
- ISBN validation
- Database migrations with Alembic
- Docker containerization
- Postman API collection included

## Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)
- Pip (package manager)

## Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/rohan-shaw/library-management-system-api.git
   ```
   ```bash
   cd library-management-system
   ```

2. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. Environment Setup

    Rename and edit template.env file to .env:

    ```env
    PROJECT_NAME=Library_Management_System
    LOG_FILE=api_requests.log
    DATABASE_URL=postgresql://user:password@localhost:port/database_name
    SECRET_KEY=your_secret_key
    ALGORITHM=encrypting algorithm e.g. HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30

    # optional
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USER=your-email
    EMAIL_PASSWORD=your-password
    EMAIL_FROM=your-email
    ```

4. Database Migrations

    ```bash
    alembic upgrade head
    ```

5. Run Server

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

## Docker Setup
1. Build and start containers:

    ```bash
    docker-compose up --build
    ```

2. Apply migrations:

    ```bash
    docker-compose exec web alembic upgrade head
    ```

## API Documentation

Available at http://localhost:8000/docs after starting the server

*Key Endpoints*

**Authentication**

`POST /register - User registration`

`POST /login - User login`

`POST /token/refresh - Refresh access token`

**Books**

`GET /books - List all books (paginated)`

`POST /books - Add new book (Admin access only)`

`PUT /books/{book_id} - Update book (Admin access only)`

**Borrowing**

`POST /borrow/{book_id} - Borrow a book`

`POST /return/{book_id} - Return a book`

`GET /borrowed - View user's borrowed books`

`GET /borrowed/details - View user's borrowed books with book detail`

**Admin**

`GET /admin/users - List all users (Admin access only)`

`GET /admin/borrowing-history - Full borrowing history (Admin access only)`

## Postman Collection

1. Import `Library_Management_System.postman_collection.json`

2. Set environment variables:

    - ` base_url` : http://localhost:8000

    - ` token` : JWT access token (obtained from login)

## Project Structure

```
├── app
│   ├── routers      # API endpoints
│   └── main.py     # FastAPI app instance
├── alembic      # Alembic migration scripts
```

## References

- [Deepseek](https://chat.deepseek.com/)
- [Fastapi docs](https://fastapi.tiangolo.com/)
- [Alembic SQLAlchemy](https://alembic.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)