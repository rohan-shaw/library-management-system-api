from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from .config import settings
from .routers import auth, books, borrow, admin
from .database import Base, get_db, engine
from jose import JWTError, jwt

app = FastAPI(
    title=settings.PROJECT_NAME
)


logging.basicConfig(
    filename=settings.LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%Y-%m %H:%M:%S",
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    path = request.url.path
    method = request.method
    user = "anonymous"

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = payload.get("sub", "unknown")  
        except JWTError:
            user = "invalid_token"

    log_message = f"Path: {path}, Method: {method}, User: {user}"
    logging.info(log_message)

    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Server Error",
            "message": str(exc),
            "path": request.url.path,
        },
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "message": exc.detail,
            "path": request.url.path,
        },
    )

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(borrow.router) 
app.include_router(admin.router) 

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Running..."}

@app.get("/database-health")
async def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "Database is healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
