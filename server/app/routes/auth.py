from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
import logging

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserLogin
from ..utils import (
    hash_password,
    verify_password,
    create_access_token,
    ALGORITHM,
)

load_dotenv()
router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SECRET_KEY = os.getenv("SECRET_KEY")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""

    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

        # Hash the password
        hashed_password = hash_password(user.password)

        # Create new user
        new_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=hashed_password,
        )

        # Save to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"Successfully registered user: {new_user.email}")
        return {
            "message": "User registered successfully",
            "email": new_user.email,
        }
    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register user")

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        )


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    Returns:
        Dict with access token and token type
    """

    try:
        # Verify if the user exists in the database
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password",
            )

        # Verify password
        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password",
            )

        # Create access token
        access_token = create_access_token(data={"sub": str(db_user.id)})

        logger.info(f"User {user.email} logged in successfully")
        return {"token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to log in")

    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        )


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Verify JWT token and return current user.

    Args:
        token: JWT access token from Authorization header
        db: Database session

    Returns:
        User object if token is valid

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception

    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        raise credentials_exception

    try:
        # Fetch user from database
        user = db.query(User).filter(User.id == int(user_id)).first()

        if user is None:
            logger.warning(f"User ID {user_id} not found in database")
            raise credentials_exception

        return user

    except ValueError:
        logger.error(f"Invalid user ID format: {user_id}")
        raise credentials_exception

    except SQLAlchemyError as e:
        logger.error(f"Database error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify user")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error fetching user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        )
