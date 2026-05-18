from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Final, List
from passlib.context import CryptContext
from Config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import jwt
from datetime import datetime, timedelta

app: Final = FastAPI()

# Define the Database Model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    hashed_password: str

# Setup Database Connection
sqlite_file_name: Final = "UsersJWT.db"
sqlite_url: Final = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Create database tables based on SQLModel schemas."""
    SQLModel.metadata.create_all(engine)
    


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
def get_session():
    with Session(engine) as session:
        yield session
        
        
        
# Using bcrypt algorithm to setup password hashing configuration 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Convert a plain password string into a secure hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)



@app.post("/register", response_model=User)
def register_user(user: User, session: Session = Depends(get_session)):
    """Register a new user by hashing their password and saving them to the DB."""
    secure_hash = hash_password(user.hashed_password)
    
    user.hashed_password = secure_hash
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_access_token(data: dict) -> str:
    """Generate a secure JWT token containing user data with an expiration time."""
    to_encode = data.copy()
    
    # Calculate when the token expires (current time + 30 minutes)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Sign the token with our secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
