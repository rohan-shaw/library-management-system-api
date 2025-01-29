from passlib.context import CryptContext
from jose import jwt
import datetime
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from .config import settings
import smtplib
from email.mime.text import MIMEText
from .main import logging

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT  
EMAIL_USER = settings.EMAIL_USER 
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
EMAIL_FROM = settings.EMAIL_FROM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def send_confirmation_email_demo(email: str, username: str):
    print(f"Sending confirmation email to {email} for user {username}")

def send_confirmation_email(email: str, username: str):
    try:
        message = MIMEText(f"Hello {username},\n\nThank you for registering!  Please confirm your email by clicking on this link: [link to confirmation page].") #Replace confirmation link
        message["Subject"] = "Welcome to our platform!"
        message["From"] = EMAIL_FROM
        message["To"] = email

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()  # Use TLS encryption
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, email, message.as_string())

        logging.info(f"Confirmation email sent to {email}")
    except Exception as e:
        logging.error(f"Error sending confirmation email to {email}: {e}")